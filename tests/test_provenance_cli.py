import json

from dslab.provenance import main


def test_cli_create_and_verify_manifest(tmp_path):
    dataset = tmp_path / "orders.csv"
    dataset.write_text("id,region\n1,west\n2,east\n", encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"dataset_name": "orders"}), encoding="utf-8")
    manifest = tmp_path / "out" / "manifest.json"
    verify_output = tmp_path / "out" / "verification.json"

    create_args = [
        "create", "--input", str(dataset), "--config", str(config),
        "--output", str(manifest),
    ]
    assert main(create_args) == 0
    assert json.loads(manifest.read_text(encoding="utf-8"))["dataset"]["row_count"] == 2

    verify_args = [
        "verify", "--manifest", str(manifest), "--output", str(verify_output)
    ]
    assert main(verify_args) == 0
    assert json.loads(verify_output.read_text(encoding="utf-8"))["status"] == "verified"


def test_cli_returns_one_for_changed_dataset(tmp_path):
    dataset = tmp_path / "orders.csv"
    dataset.write_text("id\n1\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    assert main(["create", "--input", str(dataset), "--output", str(manifest)]) == 0
    dataset.write_text("id\n2\n", encoding="utf-8")
    assert main(["verify", "--manifest", str(manifest)]) == 1


def test_cli_returns_error_for_missing_input(capsys, tmp_path):
    code = main(["create", "--input", str(tmp_path / "missing.csv")])
    assert code == 2
    assert "Error:" in capsys.readouterr().err
