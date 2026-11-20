import json

from dslab.provenance_engine import build_manifest
from dslab.provenance_report import write_json_report
from dslab.provenance_verify import verify_manifest


def create_inputs(tmp_path):
    dataset = tmp_path / "orders.csv"
    dataset.write_text("id,region\n1,west\n2,east\n", encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {"dataset_name": "orders", "purpose": "test", "tags": ["unit"]}
        ),
        encoding="utf-8",
    )
    return dataset, config


def test_manifest_contains_hashes_shape_and_metadata(tmp_path):
    dataset, config = create_inputs(tmp_path)
    manifest = build_manifest(dataset, config)
    assert manifest["manifest_version"] == 1
    assert manifest["dataset"]["sha256"]
    assert manifest["dataset"]["row_count"] == 2
    assert manifest["dataset"]["column_count"] == 2
    assert manifest["configuration"]["sha256"]
    assert manifest["metadata"]["dataset_name"] == "orders"
    assert manifest["metadata"]["tags"] == ["unit"]


def test_manifest_verifies_unchanged_sources(tmp_path):
    dataset, config = create_inputs(tmp_path)
    manifest_path = tmp_path / "nested" / "manifest.json"
    write_json_report(build_manifest(dataset, config), manifest_path)
    result = verify_manifest(manifest_path)
    assert result["status"] == "verified"
    assert result["checks_passed"] == result["checks_total"]


def test_manifest_detects_dataset_content_change(tmp_path):
    dataset, config = create_inputs(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    write_json_report(build_manifest(dataset, config), manifest_path)
    dataset.write_text("id,region\n1,west\n2,north\n", encoding="utf-8")
    result = verify_manifest(manifest_path)
    assert result["status"] == "mismatch"
    assert any(
        check["name"] == "dataset_sha256" and not check["passed"]
        for check in result["checks"]
    )


def test_manifest_detects_configuration_change(tmp_path):
    dataset, config = create_inputs(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    write_json_report(build_manifest(dataset, config), manifest_path)
    config.write_text('{"dataset_name":"changed"}', encoding="utf-8")
    result = verify_manifest(manifest_path)
    assert result["status"] == "mismatch"
    assert any(
        check["name"] == "configuration_sha256" and not check["passed"]
        for check in result["checks"]
    )
