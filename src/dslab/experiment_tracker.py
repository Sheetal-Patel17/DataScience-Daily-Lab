
"""Lightweight ML experiment tracking and reproducibility utilities."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ExperimentTracker:
    """Store, compare, and export machine-learning experiment runs."""

    SCHEMA_VERSION = 1

    def __init__(self, storage_path: str | Path) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.runs: list[dict[str, Any]] = []
        self._load()

    @staticmethod
    def fingerprint_dataset(path: str | Path) -> str:
        """Return a SHA-256 fingerprint of a dataset file."""
        file_path = Path(path)
        if not file_path.is_file():
            raise FileNotFoundError(file_path)

        digest = hashlib.sha256()
        with file_path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)

        return digest.hexdigest()

    @staticmethod
    def _validate_json_value(value: Any, field: str) -> None:
        try:
            json.dumps(value, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field} must contain valid JSON values") from exc

    @staticmethod
    def _validate_metrics(metrics: dict[str, float]) -> None:
        if not isinstance(metrics, dict) or not metrics:
            raise ValueError("metrics must be a non-empty dictionary")

        for name, value in metrics.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Metric names must be non-empty strings")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"Metric '{name}' must be numeric")
            if not math.isfinite(value):
                raise ValueError(f"Metric '{name}' must be finite")

    def _load(self) -> None:
        if not self.storage_path.exists():
            return

        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise ValueError("Experiment storage contains invalid JSON") from exc

        if not isinstance(data, dict) or data.get("schema_version") != self.SCHEMA_VERSION:
            raise ValueError("Unsupported experiment storage format")

        runs = data.get("runs")
        if not isinstance(runs, list):
            raise ValueError("Experiment storage must contain a runs list")

        self.runs = runs

    def _save(self) -> None:
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "runs": self.runs,
        }

        temp_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.storage_path.parent,
                delete=False,
                suffix=".tmp",
            ) as file:
                json.dump(payload, file, indent=2, allow_nan=False)
                file.write("\n")
                temp_path = file.name

            os.replace(temp_path, self.storage_path)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    def log_run(
        self,
        experiment_name: str,
        params: dict[str, Any],
        metrics: dict[str, float],
        *,
        seed: int | None = None,
        dataset_path: str | Path | None = None,
        dataset_fingerprint: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Record a completed experiment run."""
        if not isinstance(experiment_name, str) or not experiment_name.strip():
            raise ValueError("experiment_name must not be empty")

        if not isinstance(params, dict):
            raise ValueError("params must be a dictionary")

        self._validate_json_value(params, "params")
        self._validate_metrics(metrics)

        if seed is not None and (
            isinstance(seed, bool) or not isinstance(seed, int) or seed < 0
        ):
            raise ValueError("seed must be a non-negative integer or None")

        if tags is None:
            tags = {}
        if not isinstance(tags, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in tags.items()
        ):
            raise ValueError("tags must be a dictionary of strings")

        if dataset_path is not None and dataset_fingerprint is not None:
            raise ValueError("Provide dataset_path or dataset_fingerprint, not both")

        fingerprint = dataset_fingerprint
        if dataset_path is not None:
            fingerprint = self.fingerprint_dataset(dataset_path)

        if fingerprint is not None and (
            not isinstance(fingerprint, str)
            or len(fingerprint) != 64
            or any(char not in "0123456789abcdef" for char in fingerprint.lower())
        ):
            raise ValueError("dataset_fingerprint must be a SHA-256 hex digest")

        run = {
            "run_id": uuid.uuid4().hex[:12],
            "experiment_name": experiment_name.strip(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "params": params.copy(),
            "metrics": metrics.copy(),
            "seed": seed,
            "dataset_fingerprint": fingerprint,
            "tags": tags.copy(),
        }

        self.runs.append(run)
        self._save()
        return run.copy()

    def list_runs(
        self, experiment_name: str | None = None
    ) -> list[dict[str, Any]]:
        """Return all runs, optionally filtered by experiment name."""
        selected = self.runs
        if experiment_name is not None:
            selected = [
                run for run in self.runs
                if run["experiment_name"] == experiment_name
            ]
        return [run.copy() for run in selected]

    def compare_runs(
        self,
        metric: str,
        experiment_name: str | None = None,
        *,
        descending: bool = True,
    ) -> list[dict[str, Any]]:
        """Rank runs that contain the requested metric."""
        if not isinstance(metric, str) or not metric.strip():
            raise ValueError("metric must not be empty")

        selected = [
            run for run in self.list_runs(experiment_name)
            if metric in run["metrics"]
        ]
        return sorted(
            selected,
            key=lambda run: run["metrics"][metric],
            reverse=descending,
        )

    def best_run(
        self,
        metric: str,
        experiment_name: str | None = None,
        *,
        maximize: bool = True,
    ) -> dict[str, Any] | None:
        """Return the best run for a metric, or None if no run has it."""
        ranked = self.compare_runs(
            metric,
            experiment_name,
            descending=maximize,
        )
        return ranked[0] if ranked else None

    def export_json(self, output_path: str | Path) -> Path:
        """Export the complete experiment history as JSON."""
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "runs": self.runs,
        }
        destination.write_text(
            json.dumps(payload, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        return destination

    def export_csv(self, output_path: str | Path) -> Path:
        """Export runs as CSV with nested fields encoded as JSON."""
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)

        fields = [
            "run_id",
            "experiment_name",
            "timestamp",
            "params",
            "metrics",
            "seed",
            "dataset_fingerprint",
            "tags",
        ]

        with destination.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            for run in self.runs:
                writer.writerow({
                    **run,
                    "params": json.dumps(run["params"], sort_keys=True),
                    "metrics": json.dumps(run["metrics"], sort_keys=True),
                    "tags": json.dumps(run["tags"], sort_keys=True),
                })

        return destination
