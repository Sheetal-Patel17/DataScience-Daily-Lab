from dslab.drift_models import DriftFinding, DriftReport


def test_finding_serializes_to_dictionary():
    finding = DriftFinding(
        "added_column", "city", "medium", "absent", "string",
        "A column was added.",
    )
    assert finding.to_dict()["column"] == "city"


def test_report_without_findings_has_no_drift():
    report = DriftReport("old.csv", "new.csv", 4, 5)
    assert report.has_drift is False
    assert report.to_dict()["summary"]["findings_count"] == 0


def test_report_counts_severity_levels():
    finding = DriftFinding(
        "removed_column", "email", "high", "string", "absent",
        "A column was removed.",
    )
    report = DriftReport("old.csv", "new.csv", 4, 5, [finding])
    assert report.to_dict()["summary"]["high_count"] == 1
