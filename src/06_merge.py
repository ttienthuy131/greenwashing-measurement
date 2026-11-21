"""Join firm-level claim measures to EPA GHGRP emissions change.

Claim measures come from one scoring run (04_score.py output) over the passages
from 03_extract.py. Shares use claim passages only (labels 1, 2, 3); U and invalid
labels are counted but excluded. Emissions change uses facilities fully attributed
to one parent (sole_100pct) in 02_parse.py trend output. The two sides are kept as
separate measures; no combined greenwashing score is computed.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

CLAIMS = ("1", "2", "3")
FIELDS = [
    "fortune_rank", "company_name", "passages_scored", "claim_passages",
    "general_count", "target_count", "outcome_count", "unclear_or_invalid",
    "general_share", "outcome_share", "emissions_start_mtco2e", "emissions_end_mtco2e",
    "emissions_pct_change",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        return list(csv.DictReader(source))


def claim_measures(passages: list[dict], labels: dict[str, str]) -> dict[str, dict]:
    firms: dict[str, dict] = {}
    for passage in passages:
        label = labels.get(passage["passage_id"])
        if label is None:
            continue
        firm = firms.setdefault(str(passage["fortune_rank"]), {
            "company_name": passage["company_name"], "counts": Counter()})
        firm["counts"][label] += 1

    result = {}
    for rank, firm in firms.items():
        counts = firm["counts"]
        claims = sum(counts[c] for c in CLAIMS)
        result[rank] = {
            "fortune_rank": rank,
            "company_name": firm["company_name"],
            "passages_scored": sum(counts.values()),
            "claim_passages": claims,
            "general_count": counts["1"],
            "target_count": counts["2"],
            "outcome_count": counts["3"],
            "unclear_or_invalid": sum(n for c, n in counts.items() if c not in CLAIMS + ("0",)),
            "general_share": counts["1"] / claims if claims else None,
            "outcome_share": counts["3"] / claims if claims else None,
        }
    return result


def emissions_change(trends: list[dict[str, str]], start: int, end: int) -> dict[str, dict]:
    by_firm: dict[str, dict[int, float]] = {}
    for row in trends:
        value = row.get("sole_100pct_emissions_mtco2e")
        if value:
            by_firm.setdefault(row["fortune_rank"], {})[int(row["reporting_year"])] = float(value)

    result = {}
    for rank, years in by_firm.items():
        first, last = years.get(start), years.get(end)
        result[rank] = {
            "emissions_start_mtco2e": first,
            "emissions_end_mtco2e": last,
            "emissions_pct_change": (last - first) / first * 100 if first and last is not None else None,
        }
    return result


def merge(claims: dict[str, dict], emissions: dict[str, dict]) -> list[dict]:
    rows = []
    for rank in sorted(claims, key=int):
        empty = dict.fromkeys(["emissions_start_mtco2e", "emissions_end_mtco2e", "emissions_pct_change"])
        rows.append({**claims[rank], **emissions.get(rank, empty)})
    return rows


def plot(rows: list[dict], path: Path, run_name: str, start: int, end: int) -> int:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    points = [r for r in rows if r["general_share"] is not None and r["emissions_pct_change"] is not None]
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for r in points:
        ax.scatter(r["emissions_pct_change"], r["general_share"], color="#2f6f4f")
        ax.annotate(f"{r['company_name']} (n={r['claim_passages']})",
                    (r["emissions_pct_change"], r["general_share"]),
                    textcoords="offset points", xytext=(5, 4), fontsize=8)
    ax.axvline(0, color="grey", linewidth=0.8)
    ax.set_xlabel(f"Change in sole-parent GHGRP emissions, {start}-{end} (%)")
    ax.set_ylabel("Share of claim passages coded general (1)")
    ax.set_ylim(0, 1)
    ax.set_title(f"Claims vs. reported emissions ({run_name})", fontsize=10)
    fig.text(0.01, 0.01, "Descriptive only. Covers fully attributed facilities; not a greenwashing score.",
             fontsize=7, color="grey")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return len(points)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", type=Path, required=True, help="score CSV from 04_score.py")
    parser.add_argument("--passages", type=Path, default=Path("data/interim/passages.jsonl"))
    parser.add_argument("--trends", type=Path,
                        default=Path("data/interim/fortune_top50_energy_trends_ry2019_2023.csv"))
    parser.add_argument("--start", type=int, default=2019)
    parser.add_argument("--end", type=int, default=2023)
    parser.add_argument("--out-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    with args.passages.open(encoding="utf-8") as source:
        passages = [json.loads(line) for line in source if line.strip()]
    labels = {r["passage_id"]: r["label"] for r in read_csv(args.scores)}
    rows = merge(claim_measures(passages, labels), emissions_change(read_csv(args.trends), args.start, args.end))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    table = args.out_dir / f"firm_claims_emissions_{args.scores.stem}.csv"
    with table.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    figure = args.out_dir / f"claims_vs_emissions_{args.scores.stem}.png"
    plotted = plot(rows, figure, args.scores.stem, args.start, args.end)
    print(f"wrote {table} ({len(rows)} firms) and {figure} ({plotted} plotted)")


if __name__ == "__main__":
    main()
