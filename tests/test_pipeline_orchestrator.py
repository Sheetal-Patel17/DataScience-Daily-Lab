"""Tests for the configurable pipeline orchestrator."""
import json
import sys
from pathlib import Path

import pytest

from dslab.pipeline_orchestrator import load_config, main, run_pipeline


def step(name, code="print('ok')", **extra):
    return {"name": name, "command": [sys.executable, "-c", code], **extra}


def test_pipeline_passes_and_records_output():
    report = run_pipeline({"name": "smoke", "steps": [step("hello")]})
    assert report["status"] == "passed"
    assert report["steps_passed"] == 1
    assert report["results"][0]["stdout"].strip() == "ok"
    assert report["results"][0]["duration_seconds"] >= 0


def test_nonzero_exit_fails_pipeline():
    report = run_pipeline({"steps": [step("bad", "raise SystemExit(4)")]})
    assert report["status"] == "failed"
    assert report["results"][0]["return_code"] == 4


def test_failure_stops_later_steps_by_default():
    report = run_pipeline({"steps": [
        step("bad", "raise SystemExit(1)"),
        step("not-run"),
    ]})
    assert report["steps_run"] == 1
    assert report["stopped_early"] is True


def test_continue_on_error_runs_remaining_steps():
    report = run_pipeline({
        "continue_on_error": True,
        "steps": [step("bad", "raise SystemExit(1)"), step("good")],
    })
    assert report["steps_run"] == 2
    assert report["steps_passed"] == 1
    assert report["status"] == "failed"


def test_timeout_is_reported():
    report = run_pipeline({
        "steps": [step("slow", "import time; time.sleep(2)", timeout_seconds=0.05)]
    })
    assert report["results"][0]["status"] == "timed_out"
    assert report["status"] == "failed"


def test_missing_executable_is_reported():
    report = run_pipeline({"steps": [{"name": "missing", "command": ["definitely-not-a-real-command-xyz"]}]})
    assert report["results"][0]["status"] == "error"


@pytest.mark.parametrize("config", [
    {},
    {"steps": []},
    {"steps": ["not an object"]},
    {"steps": [{"name": "x", "command": []}]},
    {"steps": [{"name": "x", "command": ["echo", "x"], "timeout_seconds": 0}]},
    {"steps": [{"name": "x", "command": ["echo"]}, {"name": "x", "command": ["echo"]}]},
])
def test_invalid_config_is_rejected(tmp_path: Path, config):
    path = tmp_path / "pipeline.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    expected_exception = TypeError if config == {"steps": ["not an object"]} else ValueError
    with pytest.raises(expected_exception):
        load_config(path)


def test_invalid_json_is_rejected(tmp_path: Path):
    path = tmp_path / "bad.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError, match="Cannot read configuration"):
        load_config(path)


def test_cli_writes_report_and_returns_success(tmp_path: Path):
    config = tmp_path / "config.json"
    output = tmp_path / "nested" / "report.json"
    config.write_text(json.dumps({"name": "cli-test", "steps": [step("ok")]}), encoding="utf-8")
    assert main(["--config", str(config), "--output", str(output)]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "passed"


def test_cli_returns_failure_for_failed_step(tmp_path: Path):
    config = tmp_path / "config.json"
    output = tmp_path / "report.json"
    config.write_text(json.dumps({"steps": [step("bad", "raise SystemExit(2)")]}), encoding="utf-8")
    assert main(["--config", str(config), "--output", str(output)]) == 1
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "failed"


def test_pipeline_environment_is_available_to_steps():
    report = run_pipeline({
        "environment": {"DSLAB_PIPELINE_VALUE": "shared"},
        "steps": [
            step(
                "read-environment",
                "import os; print(os.environ['DSLAB_PIPELINE_VALUE'])",
            )
        ],
    })

    assert report["status"] == "passed"
    assert report["results"][0]["stdout"].strip() == "shared"


def test_step_environment_overrides_pipeline_environment():
    report = run_pipeline({
        "environment": {"DSLAB_VALUE": "pipeline"},
        "steps": [
            step(
                "override",
                "import os; print(os.environ['DSLAB_VALUE'])",
                environment={"DSLAB_VALUE": "step"},
            )
        ],
    })

    assert report["results"][0]["stdout"].strip() == "step"


def test_step_environment_preserves_pipeline_variables():
    report = run_pipeline({
        "environment": {"DSLAB_SHARED": "available"},
        "steps": [
            step(
                "combined",
                (
                    "import os; "
                    "print(os.environ['DSLAB_SHARED'] + '-' "
                    "+ os.environ['DSLAB_LOCAL'])"
                ),
                environment={"DSLAB_LOCAL": "local"},
            )
        ],
    })

    assert report["results"][0]["stdout"].strip() == "available-local"


def test_invalid_pipeline_environment_is_rejected(tmp_path):
    path = tmp_path / "pipeline.json"
    path.write_text(
        json.dumps({
            "environment": ["NOT", "A", "MAPPING"],
            "steps": [{"name": "ok", "command": ["echo", "ok"]}],
        }),
        encoding="utf-8",
    )

    with pytest.raises(TypeError, match="Pipeline environment"):
        load_config(path)


def test_non_string_environment_value_is_rejected(tmp_path):
    path = tmp_path / "pipeline.json"
    path.write_text(
        json.dumps({
            "environment": {"DSLAB_VALUE": 123},
            "steps": [{"name": "ok", "command": ["echo", "ok"]}],
        }),
        encoding="utf-8",
    )

    with pytest.raises(TypeError, match="values must be strings"):
        load_config(path)


def test_invalid_step_environment_is_rejected(tmp_path):
    path = tmp_path / "pipeline.json"
    path.write_text(
        json.dumps({
            "steps": [{
                "name": "invalid-env",
                "command": ["echo", "ok"],
                "environment": "NOT A MAPPING",
            }],
        }),
        encoding="utf-8",
    )

    with pytest.raises(TypeError, match="Step 'invalid-env' environment"):
        load_config(path)


def test_empty_environment_key_is_rejected(tmp_path):
    path = tmp_path / "pipeline.json"
    path.write_text(
        json.dumps({
            "environment": {"": "invalid"},
            "steps": [{"name": "ok", "command": ["echo", "ok"]}],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="keys must be non-empty"):
        load_config(path)


def test_each_pipeline_run_gets_a_unique_run_id():
    config = {"name": "identity-test", "steps": [step("ok")]}

    first = run_pipeline(config)
    second = run_pipeline(config)

    assert first["run_id"]
    assert second["run_id"]
    assert first["run_id"] != second["run_id"]
