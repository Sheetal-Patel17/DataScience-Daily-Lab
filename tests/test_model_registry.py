
import json

import pytest

from dslab.model_registry import ModelRegistry


@pytest.fixture
def registry(tmp_path):
    return ModelRegistry(tmp_path / "registry.json")


def test_register_model(registry):
    model = registry.register_model(
        name="RandomForest",
        model_type="classification",
        metrics={"accuracy": 0.92, "f1_score": 0.89},
        metadata={"framework": "scikit-learn"},
    )

    assert model["name"] == "RandomForest"
    assert model["version"] == 1
    assert model["stage"] == "Development"
    assert model["metrics"]["accuracy"] == 0.92


def test_model_versioning(registry):
    first = registry.register_model(
        "RandomForest", "classification", {"accuracy": 0.90}
    )
    second = registry.register_model(
        "RandomForest", "classification", {"accuracy": 0.95}
    )

    assert first["version"] == 1
    assert second["version"] == 2


def test_get_latest_model(registry):
    registry.register_model("ModelA", "regression", {"rmse": 4.2})
    registry.register_model("ModelA", "regression", {"rmse": 3.8})

    model = registry.get_model("ModelA")

    assert model["version"] == 2
    assert model["metrics"]["rmse"] == 3.8


def test_get_specific_version(registry):
    registry.register_model("ModelA", "classification", {"accuracy": 0.8})
    registry.register_model("ModelA", "classification", {"accuracy": 0.9})

    model = registry.get_model("ModelA", version=1)

    assert model["version"] == 1


def test_model_not_found(registry):
    with pytest.raises(KeyError):
        registry.get_model("UnknownModel")


def test_invalid_version(registry):
    registry.register_model("ModelA", "classification", {"accuracy": 0.8})

    with pytest.raises(KeyError):
        registry.get_model("ModelA", version=10)


def test_empty_model_name(registry):
    with pytest.raises(ValueError):
        registry.register_model("", "classification", {"accuracy": 0.9})


def test_invalid_metric_values(registry):
    with pytest.raises(ValueError):
        registry.register_model(
            "ModelA", "classification", {"accuracy": "high"}
        )


def test_update_model_stage(registry):
    registry.register_model("ModelA", "classification", {"accuracy": 0.9})

    model = registry.update_stage("ModelA", 1, "Production")

    assert model["stage"] == "Production"


def test_invalid_stage(registry):
    registry.register_model("ModelA", "classification", {"accuracy": 0.9})

    with pytest.raises(ValueError):
        registry.update_stage("ModelA", 1, "Testing")


def test_list_models(registry):
    registry.register_model("ModelA", "classification", {"accuracy": 0.9})
    registry.register_model("ModelB", "regression", {"rmse": 3.2})

    models = registry.list_models()

    assert len(models) == 2


def test_compare_models(registry):
    registry.register_model("ModelA", "classification", {"accuracy": 0.85})
    registry.register_model("ModelA", "classification", {"accuracy": 0.95})
    registry.register_model("ModelA", "classification", {"accuracy": 0.90})

    results = registry.compare_models("ModelA", "accuracy")

    assert results[0]["metrics"]["accuracy"] == 0.95
    assert results[-1]["metrics"]["accuracy"] == 0.85


def test_compare_missing_metric(registry):
    registry.register_model("ModelA", "classification", {"accuracy": 0.9})

    assert registry.compare_models("ModelA", "precision") == []


def test_registry_persistence(tmp_path):
    path = tmp_path / "registry.json"

    registry = ModelRegistry(path)
    registry.register_model("ModelA", "classification", {"accuracy": 0.9})

    loaded_registry = ModelRegistry(path)

    assert loaded_registry.get_model("ModelA")["version"] == 1


def test_registry_json_is_valid(tmp_path):
    path = tmp_path / "registry.json"

    registry = ModelRegistry(path)
    registry.register_model("ModelA", "classification", {"accuracy": 0.9})

    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    assert "ModelA" in data
