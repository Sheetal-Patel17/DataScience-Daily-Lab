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


@pytest.mark.parametrize(
    ("timestamp", "expected_exception"),
    [
        ("not-a-timestamp", ValueError),
        ("2026-11-06T10:00:00", ValueError),
        (12345, TypeError),
    ],
)
def test_invalid_started_at_utc_is_rejected(timestamp, expected_exception):
    item = report()
    item["started_at_utc"] = timestamp

    with pytest.raises(expected_exception):
        analyze_reports([item])


def test_started_at_utc_accepts_z_suffix():
    item = report()
    item["started_at_utc"] = "2026-11-06T10:00:00Z"

    result = analyze_reports([item])

    assert result["run_history"][0]["started_at_utc"].endswith("Z")


def test_missing_started_at_utc_is_supported():
    item = report()
    item.pop("started_at_utc")

    result = analyze_reports([item])

    assert result["run_history"][0]["started_at_utc"] is None



def test_duplicate_run_id_is_rejected():
    first = report()
    second = report()
    first["run_id"] = "run-123"
    second["run_id"] = "run-123"

    with pytest.raises(ValueError, match="Duplicate pipeline run ID"):
        analyze_reports([first, second])

def test_same_pipeline_at_different_times_is_allowed():
    first = report()
    second = report()
    second["started_at_utc"] = "2026-11-06T10:00:00+00:00"

    result = analyze_reports([first, second])

    assert result["runs_analyzed"] == 2


def test_different_pipelines_at_same_time_are_allowed():
    result = analyze_reports([report("alpha"), report("beta")])

    assert result["runs_analyzed"] == 2



def test_same_timestamp_with_different_run_ids_is_allowed():
    first = report()
    second = report()
    first["run_id"] = "run-123"
    second["run_id"] = "run-456"

    result = analyze_reports([first, second])

    assert result["runs_analyzed"] == 2


def test_invalid_run_id_is_rejected():
    item = report()
    item["run_id"] = " "

    with pytest.raises(ValueError, match="run_id must not be empty"):
        analyze_reports([item])

def test_reports_without_timestamps_are_not_deduplicated():
    first = report()
    second = report()
    first.pop("started_at_utc")
    second.pop("started_at_utc")

    result = analyze_reports([first, second])

    assert result["runs_analyzed"] == 2


def test_pipeline_filter_selects_only_requested_pipeline():
    reports = [
        report("alpha"),
        report("beta", status="failed"),
        report("alpha"),
    ]

    result = analyze_reports(reports, pipeline_names={"alpha"})

    assert result["runs_analyzed"] == 2
    assert result["pipelines_analyzed"] == 1
    assert result["pipeline_summaries"][0]["pipeline"] == "alpha"
    assert result["overall_success_rate_percent"] == 100.0
    assert result["analysis_metadata"]["source_report_count"] == 3
    assert result["analysis_metadata"]["analyzed_report_count"] == 2


def test_pipeline_filter_supports_multiple_names():
    reports = [
        report("alpha"),
        report("beta"),
        report("gamma"),
    ]

    result = analyze_reports(reports, pipeline_names={"alpha", "gamma"})

    assert result["runs_analyzed"] == 2
    assert result["analysis_metadata"]["selected_pipeline_names"] == [
        "alpha", "gamma"
    ]


def test_pipeline_filter_rejects_unknown_names():
    with pytest.raises(ValueError, match="No reports matched"):
        analyze_reports([report("alpha")], pipeline_names={"missing"})


def test_pipeline_filter_rejects_empty_selection():
    with pytest.raises(ValueError, match="non-empty set"):
        analyze_reports([report()], pipeline_names=set())


def test_pipeline_filter_rejects_invalid_names():
    with pytest.raises(ValueError, match="non-empty strings"):
        analyze_reports([report()], pipeline_names={""})


def test_date_filter_selects_inclusive_date_range():
    first = report()
    middle = report()
    last = report()

    first["started_at_utc"] = "2026-11-05T10:00:00+00:00"
    middle["started_at_utc"] = "2026-11-06T10:00:00+00:00"
    last["started_at_utc"] = "2026-11-07T10:00:00+00:00"

    result = analyze_reports(
        [first, middle, last],
        start_date="2026-11-06",
        end_date="2026-11-06",
    )

    assert result["runs_analyzed"] == 1
    assert result["run_history"][0]["started_at_utc"] == middle["started_at_utc"]
    assert result["analysis_metadata"]["source_report_count"] == 3
    assert result["analysis_metadata"]["analyzed_report_count"] == 1


def test_date_filter_supports_start_date_only():
    first = report()
    second = report()
    first["started_at_utc"] = "2026-11-05T10:00:00+00:00"
    second["started_at_utc"] = "2026-11-06T10:00:00+00:00"

    result = analyze_reports([first, second], start_date="2026-11-06")

    assert result["runs_analyzed"] == 1


def test_date_filter_supports_end_date_only():
    first = report()
    second = report()
    first["started_at_utc"] = "2026-11-05T10:00:00+00:00"
    second["started_at_utc"] = "2026-11-06T10:00:00+00:00"

    result = analyze_reports([first, second], end_date="2026-11-05")

    assert result["runs_analyzed"] == 1


def test_date_filter_rejects_invalid_or_reversed_dates():
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        analyze_reports([report()], start_date="not-a-date")

    with pytest.raises(ValueError, match="cannot be later"):
        analyze_reports(
            [report()],
            start_date="2026-11-07",
            end_date="2026-11-06",
        )


def test_date_filter_excludes_reports_without_timestamps():
    item = report()
    item.pop("started_at_utc")

    with pytest.raises(ValueError, match="No reports matched"):
        analyze_reports([item], start_date="2026-11-01")


def test_median_runtime_statistics():
    reports = [
        report(duration=2),
        report(duration=4),
        report(duration=100),
        report(duration=6),
    ]

    result = analyze_reports(reports)
    summary = result["pipeline_summaries"][0]

    assert summary["median_duration_seconds"] == 5.0
    assert summary["average_duration_seconds"] == 28.0
    assert summary["maximum_duration_seconds"] == 100.0


def test_median_runtime_for_single_run():
    result = analyze_reports([report(duration=7)])
    assert result["pipeline_summaries"][0]["median_duration_seconds"] == 7.0


def test_runtime_trend_detects_increased_runtime():
    reports = [
        report(duration=10),
        report(duration=12),
        report(duration=20),
        report(duration=22),
    ]
    reports[0]["started_at_utc"] = "2026-11-01T10:00:00+00:00"
    reports[1]["started_at_utc"] = "2026-11-02T10:00:00+00:00"
    reports[2]["started_at_utc"] = "2026-11-03T10:00:00+00:00"
    reports[3]["started_at_utc"] = "2026-11-04T10:00:00+00:00"

    result = analyze_reports(reports)
    trend = result["pipeline_summaries"][0]["runtime_trend"]

    assert trend["direction"] == "increased"
    assert trend["earlier_average_seconds"] == 11.0
    assert trend["recent_average_seconds"] == 21.0
    assert trend["change_percent"] == 90.9091
    assert trend["runs_compared"] == 4


def test_runtime_trend_detects_decreased_runtime():
    reports = [
        report(duration=20),
        report(duration=18),
        report(duration=10),
        report(duration=8),
    ]
    for index, item in enumerate(reports, start=1):
        item["started_at_utc"] = (
            f"2026-11-0{index}T10:00:00+00:00"
        )

    result = analyze_reports(reports)
    trend = result["pipeline_summaries"][0]["runtime_trend"]

    assert trend["direction"] == "decreased"
    assert trend["change_percent"] == -52.6316


def test_runtime_trend_handles_insufficient_timestamps():
    result = analyze_reports([report(duration=5)])
    trend = result["pipeline_summaries"][0]["runtime_trend"]

    assert trend["direction"] == "insufficient_data"
    assert trend["change_percent"] is None
    assert trend["runs_compared"] == 1


def test_success_rate_trend_detects_improvement():
    reports = [
        report(status="failed"),
        report(status="failed"),
        report(status="passed"),
        report(status="passed"),
    ]
    for index, item in enumerate(reports, start=1):
        item["started_at_utc"] = (
            f"2026-11-0{index}T10:00:00+00:00"
        )

    result = analyze_reports(reports)
    trend = result["pipeline_summaries"][0]["success_rate_trend"]

    assert trend["direction"] == "improved"
    assert trend["earlier_success_rate_percent"] == 0.0
    assert trend["recent_success_rate_percent"] == 100.0
    assert trend["change_percentage_points"] == 100.0
    assert trend["runs_compared"] == 4


def test_success_rate_trend_detects_decline():
    reports = [
        report(status="passed"),
        report(status="passed"),
        report(status="failed"),
        report(status="failed"),
    ]
    for index, item in enumerate(reports, start=1):
        item["started_at_utc"] = (
            f"2026-11-0{index}T10:00:00+00:00"
        )

    result = analyze_reports(reports)
    trend = result["pipeline_summaries"][0]["success_rate_trend"]

    assert trend["direction"] == "declined"
    assert trend["change_percentage_points"] == -100.0


def test_success_rate_trend_handles_unchanged_rate():
    reports = [
        report(status="passed"),
        report(status="failed"),
        report(status="passed"),
        report(status="failed"),
    ]
    for index, item in enumerate(reports, start=1):
        item["started_at_utc"] = (
            f"2026-11-0{index}T10:00:00+00:00"
        )

    result = analyze_reports(reports)
    trend = result["pipeline_summaries"][0]["success_rate_trend"]

    assert trend["direction"] == "unchanged"
    assert trend["change_percentage_points"] == 0.0


def test_success_rate_trend_handles_insufficient_timestamps():
    result = analyze_reports([report(status="passed")])
    trend = result["pipeline_summaries"][0]["success_rate_trend"]

    assert trend["direction"] == "insufficient_data"
    assert trend["change_percentage_points"] is None
    assert trend["runs_compared"] == 1


def test_regression_detector_flags_runtime_increase():
    reports = [
        report(duration=10),
        report(duration=10),
        report(duration=13),
        report(duration=13),
    ]
    for index, item in enumerate(reports, start=1):
        item["started_at_utc"] = (
            f"2026-11-0{index}T10:00:00+00:00"
        )

    result = analyze_reports(reports)
    flags = result["pipeline_summaries"][0]["regression_flags"]

    assert flags["runtime_regression"] is True
    assert flags["success_rate_regression"] is False
    assert flags["alerts"] == ["runtime_increase"]


def test_regression_detector_flags_success_rate_decline():
    reports = [
        report(status="passed"),
        report(status="passed"),
        report(status="failed"),
        report(status="failed"),
    ]
    for index, item in enumerate(reports, start=1):
        item["started_at_utc"] = (
            f"2026-11-0{index}T10:00:00+00:00"
        )

    result = analyze_reports(reports)
    flags = result["pipeline_summaries"][0]["regression_flags"]

    assert flags["runtime_regression"] is False
    assert flags["success_rate_regression"] is True
    assert flags["alerts"] == ["success_rate_decline"]


def test_regression_detector_supports_custom_thresholds():
    reports = [
        report(duration=10),
        report(duration=10),
        report(duration=12),
        report(duration=12),
    ]
    for index, item in enumerate(reports, start=1):
        item["started_at_utc"] = (
            f"2026-11-0{index}T10:00:00+00:00"
        )

    result = analyze_reports(
        reports,
        runtime_regression_threshold_percent=25,
    )
    flags = result["pipeline_summaries"][0]["regression_flags"]

    assert flags["runtime_regression"] is False
    assert flags["runtime_threshold_percent"] == 25


def test_regression_detector_rejects_invalid_thresholds():
    for threshold in (-1, float("inf"), float("nan"), True):
        try:
            analyze_reports(
                [report()],
                runtime_regression_threshold_percent=threshold,
            )
        except ValueError:
            continue
        raise AssertionError(f"Expected invalid threshold rejection: {threshold}")


def test_cli_loads_custom_regression_threshold_config(tmp_path):
    source = tmp_path / "reports"
    source.mkdir()

    durations = [10, 10, 13, 13]
    for index, duration in enumerate(durations, start=1):
        item = report(duration=duration)
        item["started_at_utc"] = (
            f"2026-11-0{index}T10:00:00+00:00"
        )
        (source / f"run-{index}.json").write_text(
            json.dumps(item),
            encoding="utf-8",
        )

    config = tmp_path / "thresholds.json"
    config.write_text(
        json.dumps({
            "runtime_regression_threshold_percent": 50,
            "success_rate_regression_threshold_points": 25,
        }),
        encoding="utf-8",
    )

    output = tmp_path / "analysis.json"
    assert main([
        "--input-dir", str(source),
        "--output", str(output),
        "--config", str(config),
    ]) == 0

    saved = json.loads(output.read_text(encoding="utf-8"))
    flags = saved["pipeline_summaries"][0]["regression_flags"]

    assert flags["runtime_threshold_percent"] == 50
    assert flags["success_rate_threshold_points"] == 25
    assert flags["runtime_regression"] is False


def test_cli_rejects_unknown_regression_config_setting(tmp_path):
    source = tmp_path / "reports"
    source.mkdir()
    (source / "run.json").write_text(
        json.dumps(report()),
        encoding="utf-8",
    )

    config = tmp_path / "invalid.json"
    config.write_text(
        json.dumps({"unknown_setting": 10}),
        encoding="utf-8",
    )

    try:
        main([
            "--input-dir", str(source),
            "--output", str(tmp_path / "analysis.json"),
            "--config", str(config),
        ])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("Expected CLI to reject unknown config setting.")
