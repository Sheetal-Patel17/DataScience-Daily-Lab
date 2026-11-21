
"""Lightweight JSON-backed machine learning model registry."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_STAGES = {"Development", "Staging", "Production", "Archived"}


class ModelRegistry:
    """Register, version, track, and manage machine learning models."""

    def __init__(self, storage_path: str | Path) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.models: dict[str, list[dict[str, Any]]] = {}
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            with self.storage_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("Registry data must be a JSON object.")
            self.models = data

    def _save(self) -> None:
        temporary_path = self.storage_path.with_suffix(
            self.storage_path.suffix + ".tmp"
        )
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(self.models, file, indent=4)
        temporary_path.replace(self.storage_path)

    def register_model(
        self,
        name: str,
        model_type: str,
        metrics: dict[str, float],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Register a new model version."""
        if not name.strip() or not model_type.strip():
            raise ValueError("Model name and type cannot be empty.")

        if not isinstance(metrics, dict):
            raise ValueError("Metrics must be a dictionary.")

        if not all(
            isinstance(value, (int, float)) and not isinstance(value, bool)
            for value in metrics.values()
        ):
            raise ValueError("Metric values must be numeric.")

        versions = self.models.setdefault(name, [])
        version = len(versions) + 1

        record = {
            "name": name,
            "version": version,
            "model_type": model_type,
            "metrics": metrics,
            "metadata": metadata or {},
            "stage": "Development",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        versions.append(record)
        self._save()
        return record

    def get_model(self, name: str, version: int | None = None) -> dict[str, Any]:
        """Retrieve a model version."""
        if name not in self.models or not self.models[name]:
            raise KeyError(f"Model '{name}' not found.")

        versions = self.models[name]

        if version is None:
            return versions[-1]

        for model in versions:
            if model["version"] == version:
                return model

        raise KeyError(f"Version {version} not found for '{name}'.")

    def list_models(self) -> list[dict[str, Any]]:
        """List all registered model versions."""
        return [
            model
            for versions in self.models.values()
            for model in versions
        ]

    def update_stage(
        self, name: str, version: int, stage: str
    ) -> dict[str, Any]:
        """Change the lifecycle stage of a model version."""
        if stage not in VALID_STAGES:
            raise ValueError(f"Invalid stage: {stage}")

        model = self.get_model(name, version)
        model["stage"] = stage
        self._save()
        return model

    def compare_models(
        self, name: str, metric: str
    ) -> list[dict[str, Any]]:
        """Compare model versions by a selected metric."""
        if name not in self.models:
            raise KeyError(f"Model '{name}' not found.")

        models = [
            model for model in self.models[name]
            if metric in model["metrics"]
        ]

        return sorted(
            models,
            key=lambda model: model["metrics"][metric],
            reverse=True,
        )
