"""Analyze historical JSON reports produced by the pipeline orchestrator."""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import UTC, date, datetime
from pathlib import Path
from statistics import median
from typing import Any


def validate_report(report: Any, source: str = "report") -> dict[str, Any]:
    """Validate the report fields required for historical analysis."""
    if not isinstance(report, dict):
        raise TypeError(f"{source}: report must be a JSON object.")

    pipeline = report.get("pipeline")
    if not isinstance(pipeline, str) or not pipeline.strip():
        raise ValueError(f"{source}: missing pipeline name.")

    if report.get("status") not in {"passed", "failed"}:
        raise ValueError(f"{source}: invalid pipeline status.")

    duration = report.get("duration_seconds")
    if (
        isinstance(duration, bool)
        or not isinstance(duration, (int, float))
        or not math.isfinite(duration)
        or duration < 0
    ):
        raise ValueError(f"{source}: duration_seconds must be non-negative.")

    started_at = report.get("started_at_utc")
    if started_at is not None:
        if not isinstance(started_at, str):
            raise TypeError(f"{source}: started_at_utc must be a string.")

        try:
            parsed_timestamp = datetime.fromisoformat(started_at)
        except ValueError as exc:
            raise ValueError(
                f"{source}: started_at_utc must be a valid ISO 8601 timestamp."
            ) from exc

        if (
            parsed_timestamp.tzinfo is None
            or parsed_timestamp.utcoffset() is None
        ):
            raise ValueError(
                f"{source}: started_at_utc must include timezone information."
            )

    run_id = report.get("run_id")
    if run_id is not None:
        if not isinstance(run_id, str):
            raise TypeError(f"{source}: run_id must be a string.")
        if not run_id.strip():
            raise ValueError(f"{source}: run_id must not be empty.")

    counts = ("steps_total", "steps_passed", "steps_failed")
    for field in counts:
        value = report.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{source}: {field} must be a non-negative integer.")

    if report["steps_passed"] + report["steps_failed"] > report["steps_total"]:
        raise ValueError(f"{source}: step counts exceed steps_total.")

    results = report.get("results", [])
    if not isinstance(results, list):
        raise TypeError(f"{source}: results must be a list.")

    for index, result in enumerate(results):
        if not isinstance(result, dict):
            raise TypeError(f"{source}: result {index + 1} must be an object.")
        name = result.get("name")
        if name is None:
            raise ValueError(f"{source}: result {index + 1} needs a name.")
        if not isinstance(name, str):
            raise TypeError(f"{source}: result {index + 1} name must be a string.")
        if not name.strip():
            raise ValueError(f"{source}: result {index + 1} needs a name.")

        status = result.get("status")
        if status is None:
            raise ValueError(f"{source}: result {index + 1} needs a status.")
        if not isinstance(status, str):
            raise TypeError(f"{source}: result {index + 1} status must be a string.")
    return report


def _run_identity(report: dict[str, Any]) -> str | None:
    """Return the unique ID of a pipeline run when available."""
    return report.get("run_id")



def load_reports(input_dir: Path) -> list[dict[str, Any]]:
    """Load and validate all JSON reports in a directory."""
    if not input_dir.exists() or not input_dir.is_dir():
        raise ValueError(f"Input directory does not exist: {input_dir}")

    files = sorted(input_dir.glob("*.json"))
    if not files:
        raise ValueError(f"No JSON reports found in: {input_dir}")

    reports = []
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Cannot read {path}: {exc}") from exc
        reports.append(validate_report(data, str(path)))
    return reports


def _runtime_trend(reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare average runtime in the earlier and recent halves of history."""
    timestamped = [
        item for item in reports
        if item.get("started_at_utc") is not None
    ]
    timestamped.sort(
        key=lambda item: datetime.fromisoformat(
            item["started_at_utc"]
        ).astimezone(UTC)
    )

    if len(timestamped) < 2:
        return {
            "direction": "insufficient_data",
            "earlier_average_seconds": None,
            "recent_average_seconds": None,
            "change_percent": None,
            "runs_compared": len(timestamped),
        }

    split_index = len(timestamped) // 2
    earlier = timestamped[:split_index]
    recent = timestamped[split_index:]

    earlier_average = sum(
        item["duration_seconds"] for item in earlier
    ) / len(earlier)
    recent_average = sum(
        item["duration_seconds"] for item in recent
    ) / len(recent)

    if earlier_average == 0:
        change_percent = 0.0 if recent_average == 0 else None
    else:
        change_percent = (
            (recent_average - earlier_average) / earlier_average
        ) * 100

    if recent_average > earlier_average:
        direction = "increased"
    elif recent_average < earlier_average:
        direction = "decreased"
    else:
        direction = "unchanged"

    return {
        "direction": direction,
        "earlier_average_seconds": round(earlier_average, 4),
        "recent_average_seconds": round(recent_average, 4),
        "change_percent": (
            round(change_percent, 4)
            if change_percent is not None else None
        ),
        "runs_compared": len(timestamped),
    }


def _success_rate_trend(reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare success rates across the earlier and recent halves."""
    timestamped = [
        item for item in reports
        if item.get("started_at_utc") is not None
    ]
    timestamped.sort(
        key=lambda item: datetime.fromisoformat(
            item["started_at_utc"]
        ).astimezone(UTC)
    )

    if len(timestamped) < 2:
        return {
            "direction": "insufficient_data",
            "earlier_success_rate_percent": None,
            "recent_success_rate_percent": None,
            "change_percentage_points": None,
            "runs_compared": len(timestamped),
        }

    split_index = len(timestamped) // 2
    earlier = timestamped[:split_index]
    recent = timestamped[split_index:]

    earlier_rate = (
        sum(item["status"] == "passed" for item in earlier)
        / len(earlier)
    ) * 100
    recent_rate = (
        sum(item["status"] == "passed" for item in recent)
        / len(recent)
    ) * 100

    change = recent_rate - earlier_rate

    if change > 0:
        direction = "improved"
    elif change < 0:
        direction = "declined"
    else:
        direction = "unchanged"

    return {
        "direction": direction,
        "earlier_success_rate_percent": round(earlier_rate, 4),
        "recent_success_rate_percent": round(recent_rate, 4),
        "change_percentage_points": round(change, 4),
        "runs_compared": len(timestamped),
    }


def analyze_reports(
    reports: list[dict[str, Any]],
    pipeline_names: set[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Calculate reliability, runtime, and failed-step statistics."""
    if not reports:
        raise ValueError("At least one pipeline report is required.")

    if pipeline_names is not None:
        if not isinstance(pipeline_names, set) or not pipeline_names:
            raise ValueError("pipeline_names must be a non-empty set.")
        if any(not isinstance(name, str) or not name.strip() for name in pipeline_names):
            raise ValueError("Pipeline names must be non-empty strings.")

    try:
        parsed_start = date.fromisoformat(start_date) if start_date else None
        parsed_end = date.fromisoformat(end_date) if end_date else None
    except (TypeError, ValueError) as exc:
        raise ValueError("Dates must use YYYY-MM-DD format.") from exc

    if parsed_start and parsed_end and parsed_start > parsed_end:
        raise ValueError("start_date cannot be later than end_date.")

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    failures: Counter[str] = Counter()
    seen_runs: set[str] = set()
    selected_reports: list[dict[str, Any]] = []

    for index, report in enumerate(reports, start=1):
        validate_report(report)
        identity = _run_identity(report)

        if identity is not None:
            if identity in seen_runs:
                raise ValueError(
                    f"Duplicate pipeline run ID detected at report {index}: "
                    f"{identity}."
                )
            seen_runs.add(identity)

        if pipeline_names is not None and report["pipeline"] not in pipeline_names:
            continue

        timestamp = report.get("started_at_utc")
        if parsed_start or parsed_end:
            if timestamp is None:
                continue
            run_date = datetime.fromisoformat(timestamp).astimezone(UTC).date()
            if parsed_start and run_date < parsed_start:
                continue
            if parsed_end and run_date > parsed_end:
                continue

        selected_reports.append(report)
        groups[report["pipeline"]].append(report)
        for result in report.get("results", []):
            if result["status"] != "passed":
                failures[f"{report['pipeline']}/{result['name']}"] += 1

    if not groups:
        raise ValueError("No reports matched the selected pipeline names.")

    summaries = []
    for pipeline, runs in sorted(groups.items()):
        durations = [float(run["duration_seconds"]) for run in runs]
        successes = sum(run["status"] == "passed" for run in runs)
        summaries.append({
            "pipeline": pipeline,
            "total_runs": len(runs),
            "successful_runs": successes,
            "failed_runs": len(runs) - successes,
            "success_rate_percent": round(successes / len(runs) * 100, 2),
            "average_duration_seconds": round(sum(durations) / len(durations), 4),
            "median_duration_seconds": round(median(durations), 4),
            "runtime_trend": _runtime_trend(groups[pipeline]),
            "success_rate_trend": _success_rate_trend(groups[pipeline]),
            "maximum_duration_seconds": round(max(durations), 4),
            "total_steps": sum(run["steps_total"] for run in runs),
            "total_passed_steps": sum(run["steps_passed"] for run in runs),
            "total_failed_steps": sum(run["steps_failed"] for run in runs),
        })

    history = [
        {
            "pipeline": run["pipeline"],
            "started_at_utc": run.get("started_at_utc"),
            "status": run["status"],
            "duration_seconds": run["duration_seconds"],
            "steps_total": run["steps_total"],
            "steps_passed": run["steps_passed"],
            "steps_failed": run["steps_failed"],
        }
        for run in selected_reports
    ]
    history.sort(key=lambda item: (item["started_at_utc"] or "", item["pipeline"]))

    successful = sum(run["status"] == "passed" for run in selected_reports)
    return {
        "schema_version": 1,
        "analysis_metadata": {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "source_report_count": len(reports),
            "analyzed_report_count": len(selected_reports),
            "selected_pipeline_names": sorted(groups),
            "start_date": start_date,
            "end_date": end_date,
        },
        "report_type": "pipeline-history-analysis",
        "runs_analyzed": len(selected_reports),
        "pipelines_analyzed": len(summaries),
        "overall_success_rate_percent": round(successful / len(selected_reports) * 100, 2),
        "pipeline_summaries": summaries,
        "step_failure_frequency": [
            {"step": name, "failures": count}
            for name, count in sorted(failures.items(), key=lambda item: (-item[1], item[0]))
        ],
        "run_history": history,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        reports = load_reports(args.input_dir)
        analysis = analyze_reports(reports)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(analysis, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (ValueError, OSError) as exc:
        parser.error(str(exc))

    print(
        f"Analyzed {analysis['runs_analyzed']} runs across "
        f"{analysis['pipelines_analyzed']} pipelines."
    )
    print(f"Overall success rate: {analysis['overall_success_rate_percent']}%")
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
