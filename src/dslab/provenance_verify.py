import json
from pathlib import Path

from dslab.provenance_dataset import inspect_csv
from dslab.provenance_hashing import sha256_file


def _add_check(checks: list[dict], name: str, expected, actual) -> None:
    checks.append({
        "name": name,
        "expected": expected,
        "actual": actual,
        "passed": expected == actual,
    })


def verify_manifest(manifest_path: str | Path) -> dict:
    """Check that the files recorded in a manifest still match their snapshot."""
    source = Path(manifest_path).resolve()
    manifest = json.loads(source.read_text(encoding="utf-8-sig"))
    if not isinstance(manifest, dict):
        raise TypeError("Manifest must be a JSON object.")
    if manifest.get("manifest_version") != 1:
        raise ValueError("Unsupported or missing manifest version.")

    dataset = manifest.get("dataset")
    if not isinstance(dataset, dict):
        raise TypeError("Manifest dataset metadata must be a JSON object.")
    if not dataset.get("path"):
        raise ValueError("Manifest is missing dataset path metadata.")
    dataset_path = Path(dataset["path"])
    profile = inspect_csv(dataset_path)
    checks = []
    _add_check(
        checks, "dataset_sha256", dataset.get("sha256"), sha256_file(dataset_path)
    )
    _add_check(
        checks, "dataset_size_bytes", dataset.get("size_bytes"),
        dataset_path.stat().st_size,
    )
    for key in ("row_count", "column_count", "columns", "missing_cells"):
        _add_check(checks, f"dataset_{key}", dataset.get(key), profile[key])

    configuration = manifest.get("configuration")
    if configuration is not None:
        if not isinstance(configuration, dict):
            raise TypeError("Manifest configuration metadata must be a JSON object.")
        if not configuration.get("path"):
            raise ValueError("Manifest configuration path is missing.")
        config_path = Path(configuration["path"])
        _add_check(
            checks, "configuration_sha256", configuration.get("sha256"),
            sha256_file(config_path),
        )
        _add_check(
            checks, "configuration_size_bytes", configuration.get("size_bytes"),
            config_path.stat().st_size,
        )

    return {
        "manifest_path": str(source),
        "dataset_path": str(dataset_path),
        "status": (
            "verified" if all(check["passed"] for check in checks) else "mismatch"
        ),
        "checks_passed": sum(check["passed"] for check in checks),
        "checks_total": len(checks),
        "checks": checks,
    }