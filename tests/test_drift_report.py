import json

from dslab.drift_models import DriftFinding, DriftReport
from dslab.drift_report import write_report


def test_report_writer_creates_json_and_parent_directory(tmp_path):
    report = DriftReport(
        "old.csv", "new.csv", 3, 4,
        [DriftFinding(
            "added_column", "city", "medium", "absent", "present",
            "Column city was added.",
        )],
    )
    destination = tmp_path / "nested" / "report.json"

    returned = write_report(report, destination)

    assert returned == destination
    saved = json.loads(destination.read_text(encoding="utf-8"))
    assert saved["has_drift"] is True
    assert saved["summary"]["medium_count"] == 1
