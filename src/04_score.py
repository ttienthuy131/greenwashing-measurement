#!/usr/bin/env python3
"""Score extracted passages with the dictionary baseline or a cached LLM."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from dictionary import load_dictionary

LABELS = {"0", "1", "2", "3", "U"}
INVALID = "invalid"

# A chat-completions call: (model, prompt, temperature, seed) -> (content, usage).
Call = Callable[[str, str, float, int], tuple[str, dict[str, int]]]


def read_passages(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as source:
        return [json.loads(line) for line in source if line.strip()]


def write_scores(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9.]+", "-", value).strip("-")


def parse_label(content: str) -> tuple[str, str]:
    """Return (label, rationale); malformed responses are kept as 'invalid'."""
    match = re.search(r"\{.*\}", content, re.DOTALL)
    try:
        payload = json.loads(match.group(0) if match else content)
    except json.JSONDecodeError:
        return INVALID, content.strip()[:200]
    if not isinstance(payload, dict):
        return INVALID, content.strip()[:200]
    label = str(payload.get("claim_status", "")).strip().upper()
    rationale = str(payload.get("rationale", "")).strip()
    return (label if label in LABELS else INVALID), rationale


def cache_key(model: str, prompt_sha: str, temperature: float, seed: int, text: str) -> str:
    request = json.dumps(
        [model, prompt_sha, temperature, seed, text], ensure_ascii=False
    )
    return hashlib.sha256(request.encode("utf-8")).hexdigest()


def openai_compatible_call(base_url: str, api_key: str | None) -> Call:
    """Build a client for any OpenAI-compatible endpoint (OpenAI, Ollama, vLLM)."""

    def call(model: str, prompt: str, temperature: float, seed: int) -> tuple[str, dict[str, int]]:
        body = json.dumps(
            {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "seed": seed,
                "response_format": {"type": "json_object"},
            }
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        request = urllib.request.Request(
            base_url.rstrip("/") + "/chat/completions", data=body, headers=headers
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.load(response)
        usage = payload.get("usage") or {}
        return payload["choices"][0]["message"]["content"], {
            "prompt_tokens": int(usage.get("prompt_tokens", 0)),
            "completion_tokens": int(usage.get("completion_tokens", 0)),
        }

    return call


def score_llm(
    passages: list[dict[str, Any]],
    prompt_template: str,
    model: str,
    call: Call,
    cache_dir: Path,
    temperature: float = 0.0,
    seed: int = 42,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    prompt_sha = hashlib.sha256(prompt_template.encode("utf-8")).hexdigest()
    cache_dir.mkdir(parents=True, exist_ok=True)
    stats = {"calls": 0, "cache_hits": 0, "prompt_tokens": 0, "completion_tokens": 0}
    rows = []
    for passage in passages:
        key = cache_key(model, prompt_sha, temperature, seed, passage["text"])
        cache_file = cache_dir / f"{key}.json"
        if cache_file.exists():
            record = json.loads(cache_file.read_text(encoding="utf-8"))
            stats["cache_hits"] += 1
        else:
            prompt = prompt_template.replace("{passage}", passage["text"])
            content, usage = call(model, prompt, temperature, seed)
            record = {
                "model": model,
                "prompt_sha256": prompt_sha,
                "temperature": temperature,
                "seed": seed,
                "passage_id": passage["passage_id"],
                "response": content,
                "usage": usage,
                "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            cache_file.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            stats["calls"] += 1
        for field in ("prompt_tokens", "completion_tokens"):
            stats[field] += record["usage"].get(field, 0)
        label, rationale = parse_label(record["response"])
        rows.append({"passage_id": passage["passage_id"], "label": label, "rationale": rationale})
    return rows, stats


def run_dictionary(passages_path: Path, scores_dir: Path) -> None:
    dictionary = load_dictionary()
    rows = [
        {"passage_id": p["passage_id"], "label": dictionary.classify(p["text"])}
        for p in read_passages(passages_path)
    ]
    output = scores_dir / f"dictionary_v{dictionary.version}.csv"
    write_scores(output, rows)
    print(f"wrote {len(rows)} dictionary labels to {output}")


def run_llm(args: argparse.Namespace) -> None:
    passages = read_passages(args.passages)[: args.limit]
    template = args.prompt.read_text(encoding="utf-8")
    call = openai_compatible_call(args.base_url, os.environ.get("LLM_API_KEY"))
    rows, stats = score_llm(
        passages, template, args.model, call, args.cache_dir, args.temperature, args.seed
    )
    output = args.scores_dir / f"llm_{slug(args.model)}_{args.prompt.stem}.csv"
    write_scores(output, rows)

    cost = (
        stats["prompt_tokens"] * args.input_price_per_mtok
        + stats["completion_tokens"] * args.output_price_per_mtok
    ) / 1_000_000
    run = {
        "finished_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": args.model,
        "prompt": args.prompt.name,
        "prompt_sha256": hashlib.sha256(template.encode("utf-8")).hexdigest(),
        "temperature": args.temperature,
        "seed": args.seed,
        "passages": len(rows),
        "invalid": sum(row["label"] == INVALID for row in rows),
        **stats,
        "estimated_cost_usd": round(cost, 4),
    }
    with (args.scores_dir / "llm_runs.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps(run) + "\n")
    print(json.dumps(run, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--passages", type=Path, default=Path("data/interim/passages.jsonl"))
    parser.add_argument("--scores-dir", type=Path, default=Path("data/interim/scores"))
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("dictionary", help="keyword baseline")

    llm = commands.add_parser("llm", help="LLM scoring with a JSON response cache")
    llm.add_argument("--model", required=True)
    llm.add_argument("--prompt", type=Path, default=Path("prompts/claim_status_v1.md"))
    llm.add_argument(
        "--base-url",
        default=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
        help="OpenAI-compatible endpoint, e.g. http://localhost:11434/v1 for Ollama",
    )
    llm.add_argument("--temperature", type=float, default=0.0)
    llm.add_argument("--seed", type=int, default=42)
    llm.add_argument("--limit", type=int, default=None)
    llm.add_argument("--cache-dir", type=Path, default=Path("data/cache/llm"))
    llm.add_argument("--input-price-per-mtok", type=float, default=0.0)
    llm.add_argument("--output-price-per-mtok", type=float, default=0.0)

    args = parser.parse_args()
    if args.command == "dictionary":
        run_dictionary(args.passages, args.scores_dir)
    else:
        run_llm(args)


if __name__ == "__main__":
    main()
