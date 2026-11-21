
# Day 21 – Machine Learning Model Registry

## Overview

The Model Registry is a lightweight Python component for managing machine learning model versions, metadata, evaluation metrics, and lifecycle stages.

It provides a centralized JSON-backed registry to organize and compare registered models.

## Objectives

- Register machine learning models.
- Maintain model version history.
- Store model metadata and evaluation metrics.
- Retrieve specific or latest model versions.
- Manage model lifecycle stages.
- Compare model versions using evaluation metrics.
- Persist registry records using JSON.

## Features

### 1. Model Registration
Register models with a name, model type, metrics, and optional metadata.

### 2. Version Management
Automatically assign sequential versions to models with the same name.

### 3. Lifecycle Management
Support four model stages:
- Development
- Staging
- Production
- Archived

### 4. Model Comparison
Compare model versions using a selected metric in descending order.

### 5. JSON Persistence
Save registry information to a JSON file and reload it when initializing the registry.

## Project Structure

```text
src/dslab/model_registry.py
tests/test_model_registry.py
docs/day-21-model-registry.md
configs/day-21-model-registry.json
```

## Technology Stack

- Python
- JSON
- Pytest
- pathlib
- datetime

## Testing

Run the tests using:

```bash
python -m pytest tests/test_model_registry.py -v
```

Test coverage includes:
- Model registration
- Version management
- Latest and specific version retrieval
- Invalid model and version handling
- Input validation
- Lifecycle stage updates
- Model listing
- Metric-based comparison
- JSON persistence

## Test Results

15 tests passed successfully.

## Learning Outcomes

- Understanding model registry concepts.
- Implementing version management.
- Managing model lifecycle stages.
- Working with JSON-based persistence.
- Writing unit tests with pytest.
- Building reusable Python components.

## Future Improvements

- Model artifact storage.
- Model deletion and rollback.
- Advanced lifecycle transition rules.
- REST API integration.
- Database-backed persistence.
- Model lineage and experiment integration.
