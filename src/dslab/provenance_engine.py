import json
import platform
from datetime import UTC, datetime
from pathlib import Path

from dslab.provenance_dataset import inspect_csv
from dslab.provenance_hashing import sha256_file

TOOL_VERSION = "0.1.0"


def _load_config(path: str | Path) -> tuple[dict, dict]:
    config_path = Path(path)
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(config, dict):
        raise TypeError("Provenance configuration must be a JSON object.")

    metadata = {}
    for key in ("dataset_name", "purpose", "tags"):
        if key in config:
            metadata[key] = config[key]
    for key in ("dataset_name", "purpose"):
        if key in metadata and not isinstance(metadata[key], str):
            raise TypeError(f"Configuration field must be a string: {key}")
    if "tags" in metadata and (
        not isinstance(metadata["tags"], list)
        or any(not isinstance(tag, str) for tag in metadata["tags"])
    ):
        raise TypeError("Configuration field 'tags' must be a list of strings.")
    return config, metadata


def build_manifest(
    input_path: str | Path,
    config_path: str | Path | None = None,
) -> dict:
    """Create a manifest describing the input dataset and optional config."""
    source = Path(input_path).resolve()
    profile = inspect_csv(source)
    dataset = {
        "path": str(source),
        "sha256": sha256_file(source),
        "size_bytes": source.stat().st_size,
        **profile,
    }

    configuration = None
    metadata = {
        "dataset_name": source.stem,
        "purpose": "Dataset provenance audit",
        "tags": [],
    }
    if config_path is not None:
        config_source = Path(config_path).resolve()
        _, config_metadata = _load_config(config_source)
        metadata.update(config_metadata)
        configuration = {
            "path": str(config_source),
            "sha256": sha256_file(config_source),
            "size_bytes": config_source.stat().st_size,
        }

    created_at = (
        datetime.now(UTC)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
    return {
        "manifest_version": 1,
        "created_at_utc": created_at,
        "metadata": metadata,
        "dataset": dataset,
        "configuration": configuration,
        "runtime": {
            "python_version": platform.python_version(),
            "tool_version": TOOL_VERSION,
        },
    }
