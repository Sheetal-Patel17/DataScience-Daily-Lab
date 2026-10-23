"""Write validation reports as readable JSON."""

import json
from pathlib import Path

from dslab.validation_models import ValidationReport


def write_json_report(
    report: ValidationReport,
    output_path: str | Path,
) -> Path:
    """Write the report and return the output path."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination
