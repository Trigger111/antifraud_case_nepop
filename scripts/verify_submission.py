"""Verify the local submission structure and optional downloaded data."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIMARY_FILES = (
    "case3_antifraud.ipynb",
    "TenTens_antifraud_management_brief.pptx",
    "TenTens_antifraud_dashboard.pbix",
    "README.md",
)
POWERBI_FILES = (
    "dim_date.csv",
    "fact_attribution_month.csv",
    "fact_behavior_segment.csv",
    "fact_bot_weekly.csv",
    "fact_econ_country.csv",
    "fact_fraud_alerts.csv",
    "fact_network_month.csv",
    "monitoring_rules.csv",
    "network_summary.csv",
)


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            checksum.update(chunk)
    return checksum.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-data", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []

    for relative in PRIMARY_FILES:
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing primary file: {relative}")

    for filename in POWERBI_FILES:
        path = ROOT / "powerbi_data" / filename
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing Power BI mart: powerbi_data/{filename}")

    notebook = ROOT / "case3_antifraud.ipynb"
    if notebook.exists():
        try:
            json.loads(notebook.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            errors.append(f"invalid notebook JSON: {error}")
        text = notebook.read_text(encoding="utf-8", errors="replace")
        if r"C:\Users\Miller" in text:
            errors.append("notebook contains a machine-specific absolute path")

    if args.require_data:
        manifest = json.loads(
            (ROOT / "data_manifest.json").read_text(encoding="utf-8")
        )
        for metadata in manifest["files"]:
            path = ROOT / "parquet" / metadata["name"]
            if not path.exists():
                errors.append(f"missing data file: parquet/{metadata['name']}")
                continue
            if path.stat().st_size != metadata["bytes"]:
                errors.append(f"wrong size: parquet/{metadata['name']}")
                continue
            if digest(path) != metadata["sha256"]:
                errors.append(f"wrong SHA-256: parquet/{metadata['name']}")

    if errors:
        print("Submission check FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    mode = "with Parquet data" if args.require_data else "repository files"
    print(f"Submission check passed: {mode}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
