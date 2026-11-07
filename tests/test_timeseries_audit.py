import json

import pytest

from dslab.timeseries_audit import (
    audit_rows,
    load_csv,
    main,
    parse_frequency,
)


@pytest.mark.parametrize(
    ("value", "seconds"),
    [("1s", 1), ("15m", 900), ("2h", 7200), ("1d", 86400)],
)
def test_parse_frequency(value, seconds):
    assert parse_frequency(value).total_seconds() == seconds


@pytest.mark.parametrize("value", ["0h", "-1h", "1w", "abc", "1.5h", ""])
def test_parse_frequency_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_frequency(value)


def test_parse_frequency_rejects_non_string():
    with pytest.raises(TypeError):
        parse_frequency(10)


def test_audit_reports_basic_metadata():
    rows = [
        {"timestamp": "2026-01-01T00:00:00Z", "temperature": "20"},
        {"timestamp": "2026-01-01T01:00:00Z", "temperature": "21"},
    ]

    report = audit_rows(rows)

    assert report["report_type"] == "timeseries-data-quality-audit"
    assert report["analysis_metadata"]["rows_analyzed"] == 2
    assert report["summary"]["valid_timestamps"] == 2


def test_missing_timestamps_are_reported():
    rows = [
        {"timestamp": "2026-01-01T00:00:00Z", "value": "10"},
        {"timestamp": "", "value": "11"},
    ]

    report = audit_rows(rows)

    assert report["summary"]["missing_timestamps"] == 1
    assert report["timestamp_findings"]["missing_rows"] == [3]


def test_invalid_timestamps_are_reported():
    rows = [
        {"timestamp": "2026-01-01T00:00:00Z", "value": "10"},
        {"timestamp": "not-a-date", "value": "11"},
    ]

    report = audit_rows(rows)

    assert report["summary"]["invalid_timestamps"] == 1
    assert report["timestamp_findings"]["invalid_values"][0]["row"] == 3


def test_duplicate_timestamps_are_detected():
    rows = [
        {"timestamp": "2026-01-01T00:00:00Z", "value": "10"},
        {"timestamp": "2026-01-01T00:00:00Z", "value": "11"},
    ]

    report = audit_rows(rows)

    assert report["summary"]["duplicate_timestamp_groups"] == 1
    assert report["timestamp_findings"]["duplicates"][0]["rows"] == [2, 3]


def test_out_of_order_timestamps_are_detected():
    rows = [
        {"timestamp": "2026-01-01T00:00:00Z", "value": "10"},
        {"timestamp": "2026-01-01T02:00:00Z", "value": "11"},
        {"timestamp": "2026-01-01T01:00:00Z", "value": "12"},
    ]

    report = audit_rows(rows)

    assert report["summary"]["out_of_order_records"] == 1
    assert report["timestamp_findings"]["out_of_order"][0]["row"] == 4


def test_missing_intervals_are_detected():
    rows = [
        {"timestamp": "2026-01-01T00:00:00Z", "value": "10"},
        {"timestamp": "2026-01-01T03:00:00Z", "value": "11"},
    ]

    report = audit_rows(rows, frequency="1h")

    assert report["summary"]["missing_intervals"] == 2
    assert report["timestamp_findings"]["missing_intervals"][0][
        "interval_aligned"
    ] is True


def test_non_aligned_intervals_are_flagged():
    rows = [
        {"timestamp": "2026-01-01T00:00:00Z", "value": "10"},
        {"timestamp": "2026-01-01T02:30:00Z", "value": "11"},
    ]

    report = audit_rows(rows, frequency="1h")

    finding = report["timestamp_findings"]["missing_intervals"][0]
    assert finding["interval_aligned"] is False


def test_numeric_outliers_are_detected():
    values = ["20", "21", "19", "22", "20", "21", "20", "100"]
    rows = [
        {
            "timestamp": f"2026-01-01T{index:02d}:00:00Z",
            "temperature": value,
        }
        for index, value in enumerate(values)
    ]

    report = audit_rows(rows)

    assert report["summary"]["numeric_outliers"] == 1
    assert report["numeric_outlier_findings"][0]["outliers"][0]["value"] == 100


def test_non_numeric_column_is_skipped():
    rows = [
        {"timestamp": f"2026-01-01T{index:02d}:00:00Z", "status": "normal"}
        for index in range(5)
    ]

    report = audit_rows(rows)

    assert report["numeric_outlier_findings"] == []


def test_timezone_offsets_are_normalized():
    rows = [
        {"timestamp": "2026-01-01T05:30:00+05:30", "value": "10"},
        {"timestamp": "2026-01-01T00:00:00Z", "value": "11"},
    ]

    report = audit_rows(rows)

    assert report["summary"]["duplicate_timestamp_groups"] == 1


def test_audit_rejects_empty_rows():
    with pytest.raises(ValueError, match="at least one"):
        audit_rows([])


def test_audit_rejects_non_dictionary_rows():
    with pytest.raises(TypeError, match="dictionary"):
        audit_rows(["invalid"])


def test_audit_rejects_missing_timestamp_column():
    rows = [{"date": "2026-01-01T00:00:00Z"}]

    with pytest.raises(ValueError, match="not found"):
        audit_rows(rows)


def test_load_csv_supports_utf8_bom(tmp_path):
    path = tmp_path / "sensor.csv"
    path.write_text(
        "\ufefftimestamp,value\n2026-01-01T00:00:00Z,10\n",
        encoding="utf-8",
    )

    rows = load_csv(path)

    assert rows[0]["timestamp"] == "2026-01-01T00:00:00Z"


def test_load_csv_rejects_duplicate_headers(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("timestamp,value,value\n2026-01-01,10,20\n")

    with pytest.raises(ValueError, match="duplicate"):
        load_csv(path)


def test_load_csv_rejects_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="header"):
        load_csv(path)


def test_load_csv_rejects_missing_data_rows(tmp_path):
    path = tmp_path / "header.csv"
    path.write_text("timestamp,value\n", encoding="utf-8")

    with pytest.raises(ValueError, match="at least one"):
        load_csv(path)


def test_load_csv_rejects_missing_file(tmp_path):
    with pytest.raises(ValueError, match="does not exist"):
        load_csv(tmp_path / "missing.csv")


def test_cli_writes_json_report(tmp_path):
    source = tmp_path / "sensor.csv"
    destination = tmp_path / "reports" / "audit.json"

    source.write_text(
        "timestamp,value\n"
        "2026-01-01T00:00:00Z,10\n"
        "2026-01-01T01:00:00Z,12\n",
        encoding="utf-8",
    )

    result = main([
        "--input", str(source),
        "--output", str(destination),
    ])

    assert result == 0
    report = json.loads(destination.read_text(encoding="utf-8"))
    assert report["summary"]["valid_timestamps"] == 2


def test_cli_uses_json_configuration(tmp_path):
    source = tmp_path / "sensor.csv"
    config = tmp_path / "config.json"
    destination = tmp_path / "report.json"

    source.write_text(
        "recorded_at,value\n2026-01-01T00:00:00Z,10\n",
        encoding="utf-8",
    )
    config.write_text(
        json.dumps({
            "timestamp_column": "recorded_at",
            "frequency": "30m",
        }),
        encoding="utf-8",
    )

    result = main([
        "--input", str(source),
        "--output", str(destination),
        "--config", str(config),
    ])

    assert result == 0
    report = json.loads(destination.read_text(encoding="utf-8"))
    assert report["analysis_metadata"]["timestamp_column"] == "recorded_at"
    assert report["analysis_metadata"]["expected_frequency"] == "30m"


def test_cli_rejects_unknown_configuration_keys(tmp_path):
    source = tmp_path / "sensor.csv"
    config = tmp_path / "config.json"

    source.write_text("timestamp,value\n2026-01-01T00:00:00Z,10\n")
    config.write_text('{"unknown_setting": true}')

    with pytest.raises(SystemExit) as error:
        main([
            "--input", str(source),
            "--output", str(tmp_path / "report.json"),
            "--config", str(config),
        ])

    assert error.value.code == 2
