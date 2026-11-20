"""Customer CSV cleaning pipeline for Day 2."""

import argparse
import json
import re
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "customer_id",
    "name",
    "email",
    "age",
    "city",
    "signup_date",
]


def quality_metrics(frame: pd.DataFrame) -> dict:
    """Calculate basic data-quality metrics."""
    return {
        "rows": len(frame),
        "columns": len(frame.columns),
        "missing_cells": int(frame.isna().sum().sum()),
        "duplicate_rows": int(frame.duplicated().sum()),
        "duplicate_customer_ids": int(
            frame["customer_id"].duplicated().sum()
        )
        if "customer_id" in frame.columns
        else 0,
    }


def clean_customer_data(raw: pd.DataFrame):
    """Clean valid customers and record rejection reasons."""
    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in raw.columns
    ]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    data = raw.copy()
    data["name"] = data["name"].astype("string").str.strip()
    data["email"] = data["email"].astype("string").str.strip().str.lower()
    data["city"] = data["city"].astype("string").str.strip()
    data["customer_id"] = pd.to_numeric(
        data["customer_id"], errors="coerce"
    ).astype("Int64")
    data["age"] = pd.to_numeric(data["age"], errors="coerce")
    data["signup_date"] = pd.to_datetime(
        data["signup_date"], errors="coerce"
    )

    accepted = []
    rejected = []
    seen_rows = set()
    seen_ids = set()

    for _, row in data.iterrows():
        record = row.to_dict()
        reasons = []

        signature = tuple(
            "<NA>" if pd.isna(value) else str(value)
            for value in row.tolist()
        )
        if signature in seen_rows:
            reasons.append("duplicate_complete_row")
        else:
            seen_rows.add(signature)

        customer_id = record["customer_id"]
        if pd.isna(customer_id):
            reasons.append("invalid_customer_id")
        elif int(customer_id) in seen_ids:
            reasons.append("duplicate_customer_id")
        else:
            seen_ids.add(int(customer_id))

        name = record["name"]
        if pd.isna(name) or not name:
            reasons.append("missing_name")

        email = record["email"]
        if pd.isna(email) or not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+", str(email)
        ):
            reasons.append("invalid_email")

        age = record["age"]
        if (
            pd.isna(age)
            or not float(age).is_integer()
            or not 0 <= float(age) <= 120
        ):
            reasons.append("invalid_age")

        city = record["city"]
        if pd.isna(city) or not city:
            reasons.append("missing_city")

        signup_date = record["signup_date"]
        if pd.isna(signup_date):
            reasons.append("invalid_signup_date")

        if reasons:
            record["rejection_reason"] = ";".join(reasons)
            rejected.append(record)
        else:
            record["customer_id"] = int(record["customer_id"])
            record["age"] = int(record["age"])
            record["signup_date"] = record["signup_date"].strftime("%Y-%m-%d")
            accepted.append(record)

    cleaned = pd.DataFrame(accepted, columns=REQUIRED_COLUMNS)
    rejected_columns = REQUIRED_COLUMNS + ["rejection_reason"]
    rejected_frame = pd.DataFrame(rejected, columns=rejected_columns)

    report = {
        "input_rows": len(raw),
        "cleaned_rows": len(cleaned),
        "rejected_rows": len(rejected_frame),
        "before_cleaning": quality_metrics(raw),
        "after_cleaning": quality_metrics(cleaned),
        "rejection_reasons": {},
    }

    if not rejected_frame.empty:
        counts = {}
        for reason_string in rejected_frame["rejection_reason"]:
            for reason in reason_string.split(";"):
                counts[reason] = counts.get(reason, 0) + 1
        report["rejection_reasons"] = counts

    return cleaned, rejected_frame, report


def run_pipeline(input_path: Path, output_dir: Path) -> dict:
    """Run cleaning and write CSV and JSON outputs."""
    raw = pd.read_csv(input_path)
    cleaned, rejected, report = clean_customer_data(raw)

    output_dir.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_dir / "customers_clean.csv", index=False)
    rejected.to_csv(output_dir / "customers_rejected.csv", index=False)

    with (output_dir / "quality_report.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Clean customer CSV data and report quality metrics."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    report = run_pipeline(args.input, args.output_dir)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
