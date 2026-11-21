#!/usr/bin/env python3
"""Screen Fortune energy candidates against EPA RY2023 direct-emitter data."""

from __future__ import annotations

import argparse
import csv
import io
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any

import openpyxl
from pyxlsb import open_workbook


REPORTING_YEAR = 2023
DIRECT_EMITTER_WORKBOOK = "ghgp_data_2023.xlsx"
MULTIYEAR_DIRECT_EMITTER_WORKBOOK = "ghgp_data_by_year_2023.xlsx"
TREND_START_YEAR = 2019


def normalize_name(value: Any) -> str:
    return " ".join(str(value or "").strip().upper().split())


def normalize_facility_id(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)) and float(value).is_integer():
        return str(int(value))
    return str(value).strip()


def ownership_percent(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def classify_attribution(
    owners: list[dict[str, Any]], matched_parent: str
) -> str:
    matches = [
        owner
        for owner in owners
        if normalize_name(owner["parent_company_name"]) == normalize_name(matched_parent)
    ]
    if not matches:
        return "not_matched"
    if (
        len(owners) == 1
        and len(matches) == 1
        and ownership_percent(matches[0]["ownership_percent"]) == 100
    ):
        return "sole_100pct_parent"
    return "unallocated_shared_or_partial"


def read_candidates(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        raise ValueError(f"No company candidates in {path}")
    return rows


def read_crosswalk(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        raise ValueError(f"No parent-company mappings in {path}")
    for row in rows:
        if row["review_status"] not in {"provisional", "confirmed"}:
            raise ValueError(
                f"Unsupported review status {row['review_status']!r} for "
                f"{row['fortune_company_name']!r}"
            )
    return rows


def read_direct_emissions(archive_path: Path) -> dict[str, dict[str, Any]]:
    with zipfile.ZipFile(archive_path) as archive:
        workbook_bytes = archive.read(DIRECT_EMITTER_WORKBOOK)

    workbook = openpyxl.load_workbook(
        io.BytesIO(workbook_bytes),
        read_only=True,
        data_only=True,
    )
    try:
        sheet = workbook["Direct Point Emitters"]
        header_row_number = None
        headers: list[Any] = []
        for row_number, row in enumerate(
            sheet.iter_rows(min_row=1, max_row=10, values_only=True),
            start=1,
        ):
            normalized = {normalize_name(value): index for index, value in enumerate(row)}
            if (
                "FACILITY ID" in normalized
                and "TOTAL REPORTED DIRECT EMISSIONS" in normalized
            ):
                header_row_number = row_number
                headers = list(row)
                break

        if header_row_number is None:
            raise ValueError("Could not locate facility headers in EPA direct-emitter data")

        column = {
            normalize_name(value): index
            for index, value in enumerate(headers)
            if value is not None
        }
        required = {
            "FACILITY ID",
            "FACILITY NAME",
            "STATE",
            "PRIMARY NAICS CODE",
            "TOTAL REPORTED DIRECT EMISSIONS",
        }
        missing = required - column.keys()
        if missing:
            raise ValueError(f"Missing EPA direct-emitter columns: {sorted(missing)}")

        facilities: dict[str, dict[str, Any]] = {}
        for row in sheet.iter_rows(min_row=header_row_number + 1, values_only=True):
            facility_id = normalize_facility_id(row[column["FACILITY ID"]])
            if not facility_id:
                continue
            if facility_id in facilities:
                raise ValueError(f"Duplicate EPA direct-emitter facility ID {facility_id}")

            emissions = row[column["TOTAL REPORTED DIRECT EMISSIONS"]]
            facilities[facility_id] = {
                "facility_name": row[column["FACILITY NAME"]],
                "state": row[column["STATE"]],
                "primary_naics_code": row[column["PRIMARY NAICS CODE"]],
                "direct_emissions_mtco2e": (
                    float(emissions) if emissions is not None else None
                ),
            }
        return facilities
    finally:
        workbook.close()


def read_multi_year_direct_emissions(
    archive_path: Path,
) -> dict[str, dict[int, float | None]]:
    with zipfile.ZipFile(archive_path) as archive:
        workbook_bytes = archive.read(MULTIYEAR_DIRECT_EMITTER_WORKBOOK)

    workbook = openpyxl.load_workbook(
        io.BytesIO(workbook_bytes),
        read_only=True,
        data_only=True,
    )
    try:
        sheet = workbook["Direct Point Emitters"]
        header_row_number = None
        headers: list[Any] = []
        for row_number, row in enumerate(
            sheet.iter_rows(min_row=1, max_row=10, values_only=True),
            start=1,
        ):
            normalized = {normalize_name(value): index for index, value in enumerate(row)}
            if "FACILITY ID" in normalized:
                header_row_number = row_number
                headers = list(row)
                break

        if header_row_number is None:
            raise ValueError("Could not locate facility headers in EPA multi-year data")

        column = {
            normalize_name(value): index
            for index, value in enumerate(headers)
            if value is not None
        }
        year_columns = {
            int(name[:4]): index
            for name, index in column.items()
            if name[:4].isdigit()
            and name.endswith("TOTAL REPORTED DIRECT EMISSIONS")
            and TREND_START_YEAR <= int(name[:4]) <= REPORTING_YEAR
        }
        if not year_columns:
            raise ValueError("Could not locate EPA multi-year emissions columns")

        emissions: dict[str, dict[int, float | None]] = {}
        for row in sheet.iter_rows(
            min_row=header_row_number + 1,
            values_only=True,
        ):
            facility_id = normalize_facility_id(row[column["FACILITY ID"]])
            if not facility_id:
                continue
            if facility_id in emissions:
                raise ValueError(f"Duplicate EPA multi-year facility ID {facility_id}")
            emissions[facility_id] = {
                year: (
                    float(row[index])
                    if row[index] is not None
                    else None
                )
                for year, index in year_columns.items()
            }
        return emissions
    finally:
        workbook.close()


def read_parent_companies(
    path: Path,
    reporting_year: int = REPORTING_YEAR,
) -> dict[str, list[dict[str, Any]]]:
    parent_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)

    with open_workbook(str(path)) as workbook:
        if str(reporting_year) not in workbook.sheets:
            raise ValueError(f"No reporting-year sheet {reporting_year} in {path}")

        with workbook.get_sheet(str(reporting_year)) as sheet:
            header: dict[str, int] | None = None
            for row_number, row in enumerate(sheet.rows(sparse=True)):
                values = [cell.v for cell in row[:16]]
                if header is None:
                    candidate_header = {
                        normalize_name(value): index
                        for index, value in enumerate(values)
                        if value is not None
                    }
                    required = {
                        "GHGRP FACILITY ID",
                        "REPORTING YEAR",
                        "PARENT COMPANY NAME",
                        "PARENT CO. PERCENT OWNERSHIP",
                    }
                    if required.issubset(candidate_header):
                        header = candidate_header
                    continue

                facility_id = normalize_facility_id(
                    values[header["GHGRP FACILITY ID"]]
                )
                if not facility_id:
                    continue
                reported_year = values[header["REPORTING YEAR"]]
                if int(float(reported_year)) != reporting_year:
                    continue

                parent_name = values[header["PARENT COMPANY NAME"]]
                if not parent_name:
                    continue
                parent_rows[facility_id].append(
                    {
                        "parent_company_name": str(parent_name).strip(),
                        "ownership_percent": values[
                            header["PARENT CO. PERCENT OWNERSHIP"]
                        ],
                    }
                )

            if header is None:
                raise ValueError(f"Could not locate parent-company headers in {path}")

    return dict(parent_rows)


def summarize_trends(
    candidates: list[dict[str, str]],
    crosswalk_by_rank: dict[int, list[dict[str, str]]],
    parent_company_path: Path,
    emissions_by_facility: dict[str, dict[int, float | None]],
) -> list[dict[str, Any]]:
    trend_rows: list[dict[str, Any]] = []
    for reporting_year in range(TREND_START_YEAR, REPORTING_YEAR + 1):
        parent_companies = read_parent_companies(
            parent_company_path,
            reporting_year,
        )
        for candidate in candidates:
            rank = int(candidate["fortune_rank"])
            mappings = crosswalk_by_rank[rank]
            matched_facilities: dict[str, dict[str, Any]] = {}
            for facility_id, owners in parent_companies.items():
                emissions = emissions_by_facility.get(facility_id, {}).get(
                    reporting_year
                )
                if emissions is None:
                    continue
                for mapping in mappings:
                    matched_owners = [
                        owner
                        for owner in owners
                        if normalize_name(owner["parent_company_name"])
                        == normalize_name(mapping["epa_parent_company_name"])
                    ]
                    if not matched_owners:
                        continue
                    attribution = classify_attribution(
                        owners,
                        mapping["epa_parent_company_name"],
                    )
                    if facility_id in matched_facilities:
                        raise ValueError(
                            f"Duplicate company/facility crosswalk for "
                            f"{candidate['company_name']} / {facility_id} / "
                            f"{reporting_year}"
                        )
                    matched_facilities[facility_id] = {
                        "emissions": emissions,
                        "included": attribution == "sole_100pct_parent",
                    }

            primary_rows = [
                row for row in matched_facilities.values() if row["included"]
            ]
            unallocated_rows = [
                row for row in matched_facilities.values() if not row["included"]
            ]
            trend_rows.append(
                {
                    "fortune_rank": rank,
                    "fortune_company_name": candidate["company_name"],
                    "reporting_year": reporting_year,
                    "epa_parent_company_names": "; ".join(
                        mapping["epa_parent_company_name"] for mapping in mappings
                    ),
                    "matched_facility_count_with_emissions": len(matched_facilities),
                    "sole_100pct_facility_count": len(primary_rows),
                    "sole_100pct_emissions_mtco2e": sum(
                        row["emissions"] for row in primary_rows
                    ),
                    "unallocated_facility_count": len(unallocated_rows),
                    "unallocated_gross_emissions_mtco2e": sum(
                        row["emissions"] for row in unallocated_rows
                    ),
                    "crosswalk_status": (
                        "parent-group names applied retrospectively; "
                        "review period-specific coverage and ownership"
                    ),
                }
            )
    return trend_rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse(data_dir: Path, input_dir: Path, output_dir: Path) -> None:
    candidates = read_candidates(input_dir / "fortune_top50_energy_candidates.csv")
    crosswalk = read_crosswalk(input_dir / "epa_parent_crosswalk.csv")
    direct_emissions = read_direct_emissions(
        data_dir / "2023_data_summary_spreadsheets.zip"
    )
    parent_companies = read_parent_companies(data_dir / "ghgp_data_parent_company.xlsb")
    multi_year_emissions = read_multi_year_direct_emissions(
        data_dir / "2023_data_summary_spreadsheets.zip"
    )

    candidates_by_rank = {
        int(row["fortune_rank"]): row for row in candidates
    }
    crosswalk_by_rank: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in crosswalk:
        rank = int(row["fortune_rank"])
        if rank not in candidates_by_rank:
            raise ValueError(
                f"Crosswalk rank {rank} does not exist in the Fortune candidate file"
            )
        crosswalk_by_rank[rank].append(row)

    facility_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for rank, candidate in sorted(candidates_by_rank.items()):
        mappings = crosswalk_by_rank.get(rank, [])
        if not mappings:
            raise ValueError(
                f"No EPA parent-company mapping for {candidate['company_name']!r}"
            )

        matched_facilities: dict[str, dict[str, Any]] = {}
        parent_record_count = 0
        for facility_id, owners in parent_companies.items():
            for mapping in mappings:
                matched_owners = [
                    owner
                    for owner in owners
                    if normalize_name(owner["parent_company_name"])
                    == normalize_name(mapping["epa_parent_company_name"])
                ]
                if not matched_owners:
                    continue
                parent_record_count += len(matched_owners)
                facility = direct_emissions.get(facility_id)
                if facility is None:
                    continue

                attribution = classify_attribution(
                    owners, mapping["epa_parent_company_name"]
                )
                if facility_id in matched_facilities:
                    raise ValueError(
                        f"Duplicate company/facility crosswalk for "
                        f"{candidate['company_name']} / {facility_id}"
                    )

                matched_facilities[facility_id] = {
                    "fortune_rank": rank,
                    "fortune_company_name": candidate["company_name"],
                    "epa_parent_company_name": mapping["epa_parent_company_name"],
                    "mapping_review_status": mapping["review_status"],
                    "facility_id": facility_id,
                    "facility_name": facility["facility_name"],
                    "state": facility["state"],
                    "primary_naics_code": facility["primary_naics_code"],
                    "direct_emissions_mtco2e": facility[
                        "direct_emissions_mtco2e"
                    ],
                    "reported_parent_count": len(owners),
                    "reported_ownership_percent": matched_owners[0][
                        "ownership_percent"
                    ],
                    "attribution_status": attribution,
                    "included_in_primary_screen": (
                        attribution == "sole_100pct_parent"
                    ),
                    "review_status": (
                        "confirmed_parent_match"
                        if mapping["review_status"] == "confirmed"
                        else "provisional_parent_match"
                    ),
                }

        primary_rows = [
            row
            for row in matched_facilities.values()
            if row["included_in_primary_screen"]
        ]
        unallocated_rows = [
            row
            for row in matched_facilities.values()
            if not row["included_in_primary_screen"]
        ]
        matched_ids = set(matched_facilities)
        all_candidate_ids = {
            facility_id
            for facility_id, owners in parent_companies.items()
            if any(
                normalize_name(owner["parent_company_name"])
                == normalize_name(mapping["epa_parent_company_name"])
                for owner in owners
                for mapping in mappings
            )
        }

        summary_rows.append(
            {
                "fortune_rank": rank,
                "fortune_company_name": candidate["company_name"],
                "epa_parent_company_names": "; ".join(
                    mapping["epa_parent_company_name"] for mapping in mappings
                ),
                "mapping_review_status": "; ".join(
                    sorted({mapping["review_status"] for mapping in mappings})
                ),
                "candidate_parent_records_all_reporter_types": parent_record_count,
                "candidate_parent_facilities_not_in_direct_emitter_table": len(
                    all_candidate_ids - matched_ids
                ),
                "direct_emitter_facility_count": len(matched_facilities),
                "sole_100pct_facility_count": len(primary_rows),
                "sole_100pct_emissions_mtco2e": sum(
                    row["direct_emissions_mtco2e"] or 0 for row in primary_rows
                ),
                "unallocated_facility_count": len(unallocated_rows),
                "unallocated_gross_emissions_mtco2e": sum(
                    row["direct_emissions_mtco2e"] or 0 for row in unallocated_rows
                ),
                "result_status": (
                    "reviewed parent-name crosswalk; descriptive GHGRP screen"
                    if all(
                        mapping["review_status"] == "confirmed"
                        for mapping in mappings
                    )
                    else "provisional parent-name crosswalk; descriptive GHGRP screen"
                ),
            }
        )
        facility_rows.extend(matched_facilities.values())

    summary_rows.sort(
        key=lambda row: row["sole_100pct_emissions_mtco2e"],
        reverse=True,
    )
    facility_rows.sort(key=lambda row: (row["fortune_rank"], row["facility_id"]))

    write_csv(
        output_dir / "fortune_top50_energy_facilities_ry2023.csv",
        [
            "fortune_rank",
            "fortune_company_name",
            "epa_parent_company_name",
            "mapping_review_status",
            "facility_id",
            "facility_name",
            "state",
            "primary_naics_code",
            "direct_emissions_mtco2e",
            "reported_parent_count",
            "reported_ownership_percent",
            "attribution_status",
            "included_in_primary_screen",
            "review_status",
        ],
        facility_rows,
    )
    write_csv(
        output_dir / "fortune_top50_energy_summary_ry2023.csv",
        list(summary_rows[0]),
        summary_rows,
    )
    trend_rows = summarize_trends(
        candidates,
        crosswalk_by_rank,
        data_dir / "ghgp_data_parent_company.xlsb",
        multi_year_emissions,
    )
    write_csv(
        output_dir / "fortune_top50_energy_trends_ry2019_2023.csv",
        list(trend_rows[0]),
        trend_rows,
    )

    print(
        "Descriptive GHGRP screen; parent-name matches follow the reviewed crosswalk. "
        "Results are not corporate emissions totals or greenwashing findings."
    )
    for row in summary_rows:
        emissions = row["sole_100pct_emissions_mtco2e"]
        print(
            f"{row['fortune_rank']:>2} {row['fortune_company_name']}: "
            f"{row['sole_100pct_facility_count']} sole-parent facilities, "
            f"{emissions:,.0f} mtCO2e; "
            f"{row['unallocated_facility_count']} unallocated"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--input-dir", type=Path, default=Path("data/inputs"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/interim"))
    args = parser.parse_args()
    parse(args.data_dir, args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
