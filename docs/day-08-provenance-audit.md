# Day 8: Dataset Provenance and Integrity Audit

## Purpose

Record which CSV and optional JSON configuration were used for an analysis,
then verify later that their contents still match the recorded snapshot. The
manifest includes SHA-256 digests, byte sizes, CSV shape, missing-cell counts,
configuration metadata, and the Python/tool versions.

## Create a manifest

Run from the repository root:

```powershell
python -m dslab.provenance create --input data/day-08/orders_snapshot.csv --config configs/day-08-provenance.json --output reports/day-08/provenance-manifest.json
```

## Verify an existing manifest

```powershell
python -m dslab.provenance verify --manifest reports/day-08/provenance-manifest.json --output reports/day-08/verification.json
```

Exit codes: `0` means manifest creation or verification succeeded; `1` means
verification completed but detected a mismatch; `2` means the input, manifest,
configuration, or command arguments could not be processed.

## What gets recorded

- SHA-256 and file size for the CSV source.
- Row count, column names/count, and missing-cell count.
- SHA-256 and file size for the optional configuration.
- Dataset name, purpose, and tags from the configuration.
- UTC creation timestamp and runtime version metadata.

## Important limitations

The manifest stores resolved absolute file paths, so verification expects the
files to remain at those locations. SHA-256 checks detect content changes but
do not prove that a source was trustworthy when first captured. Keep manifests
with the analysis artifacts, protect them from unauthorized edits, and review
whether the recorded inputs are the intended versions.