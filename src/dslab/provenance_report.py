import json
from pathlib import Path


def write_json_report(report: dict, output_path: str | Path) -> Path:
    """Write a JSON report and return its path."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination