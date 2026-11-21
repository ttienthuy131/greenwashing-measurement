"""Validate claim-status labels against human coding and across scoring runs.

Human labels come from CSV files shaped like data/templates/annotation_template.csv.
Machine labels come from the CSV files written by 04_score.py. The report goes to
outputs/validation.md. With no human labels, only run-to-run stability is reported.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from itertools import combinations
from pathlib import Path

LABELS = ["0", "1", "2", "3", "U"]
Labels = dict[str, str]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        return list(csv.DictReader(source))


def load_human(paths: list[Path]) -> dict[str, Labels]:
    coders: dict[str, Labels] = {}
    for path in paths:
        for row in read_csv(path):
            label = (row.get("claim_status") or "").strip().upper()
            if row.get("passage_id") and label:
                coders.setdefault(row.get("annotator_id") or path.stem, {})[row["passage_id"]] = label
    return coders


def load_runs(paths: list[Path]) -> dict[str, Labels]:
    return {path.stem: {r["passage_id"]: r["label"] for r in read_csv(path)} for path in paths}


def paired(a: Labels, b: Labels) -> list[tuple[str, str]]:
    return [(a[k], b[k]) for k in sorted(a.keys() & b.keys())]


def cohen_kappa(pairs: list[tuple[str, str]]) -> float | None:
    if not pairs:
        return None
    n = len(pairs)
    observed = sum(x == y for x, y in pairs) / n
    left, right = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    expected = sum(left[c] * right[c] for c in left) / n**2
    if expected == 1:
        return 1.0 if observed == 1 else None
    return (observed - expected) / (1 - expected)


def confusion(pairs: list[tuple[str, str]]) -> dict[str, Counter]:
    table: dict[str, Counter] = {}
    for truth, predicted in pairs:
        table.setdefault(truth, Counter())[predicted] += 1
    return table


def label_order(pairs: list[tuple[str, str]]) -> list[str]:
    seen = {x for p in pairs for x in p}
    return [c for c in LABELS if c in seen] + sorted(seen - set(LABELS))


def per_class(pairs: list[tuple[str, str]]) -> dict[str, dict[str, float | None]]:
    result = {}
    for label in label_order(pairs):
        hit = sum(t == p == label for t, p in pairs)
        predicted = sum(p == label for _, p in pairs)
        actual = sum(t == label for t, _ in pairs)
        result[label] = {
            "precision": hit / predicted if predicted else None,
            "recall": hit / actual if actual else None,
            "support": actual,
        }
    return result


def fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def kappa_table(title: str, pairs_by_name: dict[tuple[str, str], list]) -> list[str]:
    lines = [f"## {title}", "", "| A | B | n | agreement | kappa |", "|---|---|---:|---:|---:|"]
    for (a, b), pairs in pairs_by_name.items():
        agreement = sum(x == y for x, y in pairs) / len(pairs) if pairs else None
        lines.append(f"| {a} | {b} | {len(pairs)} | {fmt(agreement)} | {fmt(cohen_kappa(pairs))} |")
    return lines + [""]


def method_section(name: str, pairs: list[tuple[str, str]]) -> list[str]:
    lines = [f"### {name}", "", f"n = {len(pairs)}, kappa = {fmt(cohen_kappa(pairs))}", ""]
    labels = label_order(pairs)
    table = confusion(pairs)
    lines += ["| human \\ model | " + " | ".join(labels) + " |", "|---" * (len(labels) + 1) + "|"]
    lines += [f"| {t} | " + " | ".join(str(table.get(t, Counter())[p]) for p in labels) + " |" for t in labels]
    lines += ["", "| label | precision | recall | support |", "|---|---:|---:|---:|"]
    lines += [
        f"| {label} | {fmt(m['precision'])} | {fmt(m['recall'])} | {m['support']} |"
        for label, m in per_class(pairs).items()
    ]
    return lines + [""]


def build_report(human: dict[str, Labels], runs: dict[str, Labels], reference: str | None) -> str:
    lines = ["# Validation report", "", f"Human coders: {len(human)}. Scoring runs: {len(runs)}.", ""]
    if len(human) > 1:
        lines += kappa_table("Human inter-coder agreement", {
            (a, b): paired(human[a], human[b]) for a, b in combinations(sorted(human), 2)
        })
    if human:
        ref = reference or sorted(human)[0]
        lines += [f"## Methods against human reference `{ref}`", ""]
        for name in sorted(runs):
            lines += method_section(name, paired(human[ref], runs[name]))
    else:
        lines += ["No human labels found, so accuracy against human coding is not reported.", ""]
    if len(runs) > 1:
        lines += kappa_table("Stability across scoring runs", {
            (a, b): paired(runs[a], runs[b]) for a, b in combinations(sorted(runs), 2)
        })
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--human", type=Path, nargs="*", default=sorted(Path("data/annotations").glob("*.csv")))
    parser.add_argument("--runs", type=Path, nargs="*", default=sorted(Path("data/interim/scores").glob("*.csv")))
    parser.add_argument("--reference", help="annotator_id used as ground truth (default: first coder)")
    parser.add_argument("--out", type=Path, default=Path("outputs/validation.md"))
    args = parser.parse_args()

    human = load_human(args.human)
    if args.reference and args.reference not in human:
        parser.error(f"unknown reference coder: {args.reference}")
    report = build_report(human, load_runs(args.runs), args.reference)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
