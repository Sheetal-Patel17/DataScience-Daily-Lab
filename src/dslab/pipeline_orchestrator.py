"""Run a configured sequence of subprocess steps and write a JSON summary."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


def _validate_environment(environment: Any, label: str) -> None:
    """Validate environment-variable mappings."""
    if environment is None:
        return

    if not isinstance(environment, dict):
        raise TypeError(f"{label} must be an object.")

    for key, value in environment.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{label} keys must be non-empty strings.")
        if not isinstance(value, str):
            raise TypeError(f"{label} values must be strings.")


def load_config(path: Path) -> dict[str, Any]:
    """Load and validate the pipeline configuration."""
    try:
        config = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read configuration: {exc}") from exc

    if not isinstance(config, dict):
        raise TypeError("Configuration must be a JSON object.")

    _validate_environment(config.get("environment"), "Pipeline environment")

    steps = config.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError("'steps' must be a non-empty list.")

    names: set[str] = set()

    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            raise TypeError(f"Step {index + 1} must be an object.")

        name = step.get("name")
        command = step.get("command")

        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Step {index + 1} needs a non-empty name.")

        if name in names:
            raise ValueError(f"Duplicate step name: {name}")

        names.add(name)

        if (
            not isinstance(command, list)
            or not command
            or any(not isinstance(part, str) or not part for part in command)
        ):
            raise ValueError(
                f"Step '{name}' command must be a non-empty string list."
            )

        timeout = step.get("timeout_seconds", 60)
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or timeout <= 0
        ):
            raise ValueError(
                f"Step '{name}' timeout_seconds must be positive."
            )

        _validate_environment(
            step.get("environment"),
            f"Step '{name}' environment",
        )

    return config


def run_pipeline(config: dict[str, Any]) -> dict[str, Any]:
    """Execute steps sequentially without invoking a shell."""
    results: list[dict[str, Any]] = []
    pipeline_started = time.monotonic()
    stopped_early = False
    pipeline_environment = os.environ.copy()
    pipeline_environment.update(config.get("environment", {}))

    for step in config["steps"]:
        started = time.monotonic()
        step_environment = pipeline_environment.copy()
        step_environment.update(step.get("environment", {}))

        result: dict[str, Any] = {
            "name": step["name"],
            "command": step["command"],
            "status": "failed",
            "return_code": None,
            "duration_seconds": 0.0,
            "stdout": "",
            "stderr": "",
            "error": None,
        }

        try:
            completed = subprocess.run(
                step["command"],
                capture_output=True,
                text=True,
                timeout=step.get("timeout_seconds", 60),
                check=False,
                shell=False,
                env=step_environment,
            )
            result.update(
                return_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                status="passed" if completed.returncode == 0 else "failed",
            )
        except subprocess.TimeoutExpired as exc:
            result.update(
                status="timed_out",
                stdout=_as_text(exc.stdout),
                stderr=_as_text(exc.stderr),
                error=(
                    f"Timed out after "
                    f"{step.get('timeout_seconds', 60)} seconds"
                ),
            )
        except OSError as exc:
            result.update(status="error", error=str(exc))
        finally:
            result["duration_seconds"] = round(
                time.monotonic() - started, 4
            )

        results.append(result)

        if (
            result["status"] != "passed"
            and not config.get("continue_on_error", False)
        ):
            stopped_early = len(results) < len(config["steps"])
            break

    failed = sum(item["status"] != "passed" for item in results)

    return {
        "run_id": str(uuid4()),
        "pipeline": config.get("name", "unnamed-pipeline"),
        "started_at_utc": datetime.now(UTC).isoformat(),
        "status": (
            "passed"
            if failed == 0 and len(results) == len(config["steps"])
            else "failed"
        ),
        "steps_total": len(config["steps"]),
        "steps_run": len(results),
        "steps_passed": sum(
            item["status"] == "passed" for item in results
        ),
        "steps_failed": failed,
        "stopped_early": stopped_early,
        "duration_seconds": round(
            time.monotonic() - pipeline_started, 4
        ),
        "results": results,
    }


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        required=True,
        type=Path,
        help="Pipeline JSON configuration",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="JSON report destination",
    )
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
        report = run_pipeline(config)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (ValueError, TypeError, OSError) as exc:
        parser.error(str(exc))

    print(
        f"{report['pipeline']}: {report['status']} "
        f"({report['steps_passed']}/{report['steps_total']} steps passed)"
    )
    print(f"Report: {args.output}")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
