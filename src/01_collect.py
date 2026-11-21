#!/usr/bin/env python3
"""Download and checksum the public EPA GHGRP pilot source files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SOURCES = (
    {
        "id": "epa_ghgrp_2023_summary",
        "url": "https://www.epa.gov/system/files/other-files/2024-10/2023_data_summary_spreadsheets.zip",
        "filename": "2023_data_summary_spreadsheets.zip",
        "required_member": None,
    },
    {
        "id": "epa_ghgrp_parent_companies",
        "url": "https://www.epa.gov/system/files/other-files/2024-10/ghgp_data_parent_company.xlsb",
        "filename": "ghgp_data_parent_company.xlsb",
        "required_member": "xl/workbook.bin",
    },
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_archive(path: Path, required_member: str | None) -> None:
    if not zipfile.is_zipfile(path):
        raise ValueError(f"Downloaded file is not a valid ZIP-based workbook: {path}")

    with zipfile.ZipFile(path) as archive:
        corrupt_member = archive.testzip()
        if corrupt_member is not None:
            raise ValueError(f"Corrupt archive member {corrupt_member!r} in {path}")
        if required_member is not None and required_member not in archive.namelist():
            raise ValueError(f"Expected workbook member {required_member!r} in {path}")


def download(url: str, destination: Path, required_member: str | None) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "greenwashing-measurement research project"},
    )
    temporary_path: Path | None = None

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            if response.status != 200:
                raise OSError(f"Unexpected HTTP status {response.status} for {url}")

            with tempfile.NamedTemporaryFile(
                dir=destination.parent,
                prefix=f"{destination.name}.",
                suffix=".part",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                for chunk in iter(lambda: response.read(1024 * 1024), b""):
                    temporary_file.write(chunk)

        if temporary_path.stat().st_size == 0:
            raise OSError(f"Downloaded an empty file from {url}")
        validate_archive(temporary_path, required_member)
        os.replace(temporary_path, destination)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary_path, path)


def collect(output_dir: Path, refresh: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    previous_manifest = read_manifest(manifest_path)
    entries: dict[str, Any] = {}

    for source in SOURCES:
        destination = output_dir / source["filename"]
        previous_entry = previous_manifest.get("files", {}).get(source["id"], {})
        downloaded_at = previous_entry.get("downloaded_at_utc")

        if refresh or not destination.exists():
            download(source["url"], destination, source["required_member"])
            downloaded_at = utc_now()
        else:
            validate_archive(destination, source["required_member"])

        entries[source["id"]] = {
            "url": source["url"],
            "filename": destination.name,
            "downloaded_at_utc": downloaded_at,
            "verified_at_utc": utc_now(),
            "bytes": destination.stat().st_size,
            "sha256": sha256_file(destination),
        }

    write_manifest(
        manifest_path,
        {
            "reporting_year": 2023,
            "files": entries,
        },
    )

    for source in SOURCES:
        entry = entries[source["id"]]
        print(f"{entry['filename']}: {entry['bytes']} bytes, sha256 {entry['sha256']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw"),
        help="directory for local source files (default: data/raw)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="download fresh copies even if source files already exist",
    )
    args = parser.parse_args()
    collect(args.output_dir, args.refresh)


if __name__ == "__main__":
    main()
