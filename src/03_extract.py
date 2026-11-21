#!/usr/bin/env python3
"""Extract climate-related passages from locally downloaded report PDFs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Iterator

from pypdf import PdfReader

from dictionary import Dictionary, load_dictionary

SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"“])")


def clean(text: str) -> str:
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    return " ".join(text.split())


def split_passages(page_text: str, max_words: int = 150) -> list[str]:
    """Split page text into paragraph-like passages of at most max_words."""
    passages: list[str] = []
    for block in re.split(r"\n\s*\n", page_text):
        block = clean(block)
        if not block:
            continue
        if len(block.split()) <= max_words:
            passages.append(block)
            continue
        current: list[str] = []
        for sentence in SENTENCE_END.split(block):
            if current and len(" ".join(current + [sentence]).split()) > max_words:
                passages.append(" ".join(current))
                current = []
            current.append(sentence)
        if current:
            passages.append(" ".join(current))
    return passages


def climate_passages(
    pages: list[str],
    dictionary: Dictionary,
    min_words: int,
    max_words: int,
) -> Iterator[tuple[int, str]]:
    for page_number, page_text in enumerate(pages, start=1):
        for passage in split_passages(page_text, max_words):
            if len(passage.split()) >= min_words and dictionary.is_climate(passage):
                yield page_number, passage


def passage_id(rank: str, page: int, text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    return f"{rank}-p{page:03d}-{digest}"


def extract(
    register: Path,
    reports_dir: Path,
    output: Path,
    min_words: int,
    max_words: int,
) -> None:
    dictionary = load_dictionary()
    with register.open(encoding="utf-8-sig", newline="") as source:
        reports = list(csv.DictReader(source))

    output.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with output.open("w", encoding="utf-8") as destination:
        for report in reports:
            rank = report["fortune_rank"]
            pdf_path = reports_dir / f"{rank}.pdf"
            if not pdf_path.exists():
                print(f"skip {report['company_name']}: {pdf_path} not found")
                continue
            pages = [page.extract_text() or "" for page in PdfReader(pdf_path).pages]
            count = 0
            for page, text in climate_passages(pages, dictionary, min_words, max_words):
                record = {
                    "passage_id": passage_id(rank, page, text),
                    "fortune_rank": int(rank),
                    "company_name": report["company_name"],
                    "report_title": report["report_title"],
                    "covered_reporting_years": report["covered_reporting_years"],
                    "page": page,
                    "text": text,
                    "dictionary_version": dictionary.version,
                }
                destination.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
            print(f"{report['company_name']}: {len(pages)} pages, {count} climate passages")
            total += count
    print(f"wrote {total} passages to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=Path("data/inputs/pilot_reports.csv"))
    parser.add_argument("--reports-dir", type=Path, default=Path("data/raw/reports"))
    parser.add_argument("--output", type=Path, default=Path("data/interim/passages.jsonl"))
    parser.add_argument("--min-words", type=int, default=25)
    parser.add_argument("--max-words", type=int, default=150)
    args = parser.parse_args()
    extract(args.register, args.reports_dir, args.output, args.min_words, args.max_words)


if __name__ == "__main__":
    main()
