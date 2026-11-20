"""Normalization helpers for CSV audit comparisons."""
import csv
import hashlib
import json
from pathlib import Path


def read_csv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        headers = [name.strip() for name in reader.fieldnames]
        if any(not name for name in headers):
            raise ValueError(f"CSV contains an empty column name: {path}")
        if len(set(headers)) != len(headers):
            raise ValueError(f"CSV contains duplicate column names: {path}")
        rows = []
        for number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"Extra fields at row {number}: {path}")
            if any(value is None for value in row.values()):
                raise ValueError(f"Missing fields at row {number}: {path}")
            rows.append({
                key.strip(): (value or "").strip()
                for key, value in row.items()
            })
        return headers, rows


def normalize_value(value: str) -> str:
    return " ".join(value.casefold().split())


def row_fingerprint(row: dict[str, str], columns: list[str]) -> str:
    normalized = [normalize_value(row.get(column, "")) for column in columns]
    payload = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
