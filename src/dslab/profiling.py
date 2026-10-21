"""Reusable CSV data profiling and HTML reporting."""

import argparse
import html
from pathlib import Path

import pandas as pd


def profile_dataframe(frame: pd.DataFrame) -> dict:
    """Calculate dataset-level and per-column quality statistics."""
    column_profiles = []

    for column in frame.columns:
        series = frame[column]
        missing = int(series.isna().sum())
        profile = {
            "name": str(column),
            "dtype": str(series.dtype),
            "missing_count": missing,
            "missing_pct": round(missing / len(frame) * 100, 2)
            if len(frame)
            else 0.0,
            "unique_count": int(series.nunique(dropna=True)),
        }

        if pd.api.types.is_numeric_dtype(series):
            profile["minimum"] = (
                round(float(series.min()), 2) if series.notna().any() else None
            )
            profile["maximum"] = (
                round(float(series.max()), 2) if series.notna().any() else None
            )
            profile["mean"] = (
                round(float(series.mean()), 2) if series.notna().any() else None
            )

        column_profiles.append(profile)

    return {
        "row_count": len(frame),
        "column_count": len(frame.columns),
        "missing_cells": int(frame.isna().sum().sum()),
        "duplicate_rows": int(frame.duplicated().sum()),
        "column_profiles": column_profiles,
    }


def generate_html_report(profile: dict, output_path: Path) -> None:
    """Write a self-contained HTML report."""
    headers = [
        "Column",
        "Data type",
        "Missing",
        "Missing %",
        "Unique values",
        "Minimum",
        "Maximum",
        "Mean",
    ]

    rows = []
    for item in profile["column_profiles"]:
        values = [
            item["name"],
            item["dtype"],
            item["missing_count"],
            f'{item["missing_pct"]}%',
            item["unique_count"],
            item.get("minimum", "—"),
            item.get("maximum", "—"),
            item.get("mean", "—"),
        ]
        cells = "".join(
            f"<td>{html.escape(str(value))}</td>" for value in values
        )
        rows.append(f"<tr>{cells}</tr>")

    header_html = "".join(
        f"<th>{html.escape(header)}</th>" for header in headers
    )
    table_rows = "\n".join(rows)

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CSV Data Profile Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #202938;
       background: #f5f7fb; }}
h1 {{ margin-bottom: 8px; }}
p {{ color: #526176; }}
.cards {{ display: flex; flex-wrap: wrap; gap: 16px; margin: 24px 0; }}
.card {{ background: white; padding: 20px; border-radius: 12px;
         box-shadow: 0 2px 8px #17203312; min-width: 140px; }}
.value {{ font-size: 28px; font-weight: bold; margin-top: 8px; }}
.table-wrap {{ overflow-x: auto; background: white; border-radius: 12px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e9f0; }}
th {{ background: #eaf0f8; }}
tr:hover {{ background: #f8fafc; }}
</style>
</head>
<body>
<h1>CSV Data Profile Report</h1>
<p>Automated overview of dataset structure and data quality.</p>
<div class="cards">
<div class="card">Rows<div class="value">{profile["row_count"]}</div></div>
<div class="card">Columns<div class="value">{profile["column_count"]}</div></div>
<div class="card">Missing cells<div class="value">{profile["missing_cells"]}</div></div>
<div class="card">Duplicate rows<div class="value">{profile["duplicate_rows"]}</div></div>
</div>
<h2>Column details</h2>
<div class="table-wrap">
<table>
<thead><tr>{header_html}</tr></thead>
<tbody>{table_rows}</tbody>
</table>
</div>
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")


def profile_csv(input_path: Path, output_path: Path) -> dict:
    """Read a CSV, profile it, and write an HTML report."""
    frame = pd.read_csv(input_path)
    profile = profile_dataframe(frame)
    generate_html_report(profile, output_path)
    return profile


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Profile a CSV and generate an HTML report."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    profile = profile_csv(args.input, args.output)
    print("CSV profiling completed successfully.")
    print(f'Rows: {profile["row_count"]}')
    print(f'Columns: {profile["column_count"]}')
    print(f'Missing cells: {profile["missing_cells"]}')
    print(f'Duplicate rows: {profile["duplicate_rows"]}')
    print(f"HTML report: {args.output}")


if __name__ == "__main__":
    main()
