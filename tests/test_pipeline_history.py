import json
from pathlib import Path

import pytest

from dslab.pipeline_history import analyze_reports, load_reports, main


def report(pipeline="demo", status="passed", duration=2.0, failed=0, results=None):
    return {
        "pipeline": pipeline,
        "started_at_utc": "2026-11-05T10:00:00+00:00",
        "status": status,
        "duration_seconds": duration,
        "steps_total": 3,
        "steps_passed": 3 - failed,
        "steps_failed": failed,
        "results": results or [],
    }


def test_success_rate():
    result = analyze_reports([
        report(), report(status="failed"), report()
    ])
    assert result["overall_success_rate_percent"] == pytest.approx(66.67)


def test_runtime_statistics():
    result = analyze_reports([report(duration=2), report(duration=4)])
    summary = result["pipeline_summaries"][0]
    assert summary["average_duration_seconds"] == 3
    assert summary["maximum_duration_seconds"] == 4


def test_pipelines_are_grouped():
    result = analyze_reports([
        report("alpha"), report("beta"), report("alpha")
    ])
    assert result["pipelines_analyzed"] == 2
    assert result["pipeline_summaries"][0]["total_runs"] == 2


def test_failed_step_frequency():
    result = analyze_reports([
        report(status="failed", failed=1,
               results=[{"name": "validate", "status": "failed"}]),
        report(status="failed", failed=1,
               results=[{"name": "validate", "status": "timed_out"}]),
    ])
    assert result["step_failure_frequency"] == [
        {"step": "demo/validate", "failures": 2}
    ]


def test_history_is_sorted():
    older = report()
    newer = report()
    older["started_at_utc"] = "2026-11-01T10:00:00+00:00"
    newer["started_at_utc"] = "2026-11-05T10:00:00+00:00"
    result = analyze_reports([newer, older])
    assert result["run_history"][0]["started_at_utc"].startswith("2026-11-01")


@pytest.mark.parametrize("item", [
    {},
    {**report(), "status": "unknown"},
    {**report(), "duration_seconds": -1},
    {**report(), "duration_seconds": float("nan")},
    {**report(), "steps_passed": 4},
])
def test_invalid_reports_are_rejected(item):
    with pytest.raises(ValueError):
        analyze_reports([item])


@pytest.mark.parametrize(
    ("item", "expected_exception"),
    [
        ("not an object", TypeError),
        ({**report(), "results": "not a list"}, TypeError),
        ({**report(), "results": ["not an object"]}, TypeError),
        ({**report(), "results": [{"status": "passed"}]}, ValueError),
        ({**report(), "results": [{"name": "step"}]}, ValueError),
    ],
)
def test_invalid_report_types_are_rejected(item, expected_exception):
    with pytest.raises(expected_exception):
        analyze_reports([item])


def test_empty_reports_are_rejected():
    with pytest.raises(ValueError):
        analyze_reports([])


def test_load_reports(tmp_path: Path):
    (tmp_path / "one.json").write_text(json.dumps(report()), encoding="utf-8")
    assert len(load_reports(tmp_path)) == 1


def test_load_reports_accepts_bom(tmp_path: Path):
    (tmp_path / "bom.json").write_text(
        "\ufeff" + json.dumps(report()), encoding="utf-8"
    )
    assert len(load_reports(tmp_path)) == 1


def test_empty_directory_is_rejected(tmp_path: Path):
    with pytest.raises(ValueError, match="No JSON reports"):
        load_reports(tmp_path)


def test_cli_writes_report(tmp_path: Path):
    source = tmp_path / "runs"
    source.mkdir()
    (source / "one.json").write_text(json.dumps(report()), encoding="utf-8")
    output = tmp_path / "nested" / "analysis.json"
    assert main(["--input-dir", str(source), "--output", str(output)]) == 0
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["runs_analyzed"] == 1


def test_analysis_output_includes_versioned_metadata():
    result = analyze_reports([report(), report(status="failed")])

    assert result["schema_version"] == 1
    assert result["analysis_metadata"]["source_report_count"] == 2
    generated_at = result["analysis_metadata"]["generated_at_utc"]
    assert generated_at.endswith("+00:00")
