# Day 9: Dataset Splitter and Leakage Guard

## Purpose

Create reproducible train, validation, and test CSV files. The tool supports
random splitting, target stratification, and group-aware splitting so repeated
entities can stay in a single partition.

## Run a group-aware split

From the repository root:

```powershell
python -m dslab.dataset_split --input data/day-09/orders_labeled.csv --config configs/day-09-split.json --output-dir reports/day-09/splits --group-column customer_id
```

## Run a stratified split

Use this when a target column has labels that should be represented in each
partition. Every target value must have at least three rows.

```powershell
python -m dslab.dataset_split --input data/day-09/orders_labeled.csv --config configs/day-09-split.json --output-dir reports/day-09/stratified --stratify-by returned
```

## Outputs

The output directory contains `train.csv`, `validation.csv`, `test.csv`, and
`split-report.json`. The report records the seed, selected mode, requested and
actual ratios, per-split counts, target-label counts when stratified, and checks
for exact duplicate rows shared between partitions.

## Ratios and reproducibility

Defaults live in `configs/day-09-split.json`. The defaults are 70% train, 15%
validation, and 15% test with seed 42. Ratios must be positive and add to 1.0.
The same input, mode, configuration, and seed produce the same row assignments.
Command-line ratio and seed flags override the config values.

## Preventing leakage

Use `--group-column` when rows from one customer, patient, account, or other
entity must not cross partitions. Group-aware splits keep all rows with a group
value together; resulting row counts may differ from requested ratios. Blank
group values are rejected. A separate exact-row check warns if an identical row
appears in more than one split.

## Limitations

Random and stratified splitting are not appropriate for every time-dependent
prediction problem. Temporal data may require chronological splitting. Exact
row overlap checks do not detect all forms of target leakage, and group-aware
splitting cannot guarantee that every source of indirect leakage is removed.
Review the report before training a model.