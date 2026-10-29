import pytest

from dslab.split_engine import DEFAULT_RATIOS, split_dataset


def make_rows(count=24):
    rows = []
    for index in range(count):
        customer = f"C{index // 4 + 1:03d}"
        rows.append({
            "order_id": f"O{index + 1:04d}",
            "customer_id": customer,
            "region": ("west", "east", "north", "south")[index % 4],
            "returned": "yes" if index % 4 == 0 else "no",
        })
    return rows


def test_random_split_is_deterministic_and_nonempty():
    rows = make_rows()
    first = split_dataset(rows, list(rows[0]), DEFAULT_RATIOS, seed=42)
    second = split_dataset(rows, list(rows[0]), DEFAULT_RATIOS, seed=42)
    assert first == second
    assert [len(first[name]) for name in ("train", "validation", "test")] == [17, 4, 3]
    assert all(first.values())


def test_different_seed_changes_order():
    rows = make_rows()
    first = split_dataset(rows, list(rows[0]), DEFAULT_RATIOS, seed=42)
    second = split_dataset(rows, list(rows[0]), DEFAULT_RATIOS, seed=7)
    assert first != second


def test_stratified_split_keeps_each_label_in_each_split():
    rows = make_rows()
    splits = split_dataset(rows, list(rows[0]), DEFAULT_RATIOS, seed=42, stratify_by="returned")
    for name in ("train", "validation", "test"):
        labels = {row["returned"] for row in splits[name]}
        assert labels == {"yes", "no"}


def test_group_split_never_separates_same_customer():
    rows = make_rows()
    splits = split_dataset(rows, list(rows[0]), DEFAULT_RATIOS, seed=42, group_column="customer_id")
    owners = {}
    for split_name, split_rows in splits.items():
        for row in split_rows:
            if row["customer_id"] in owners:
                assert owners[row["customer_id"]] == split_name
            owners[row["customer_id"]] = split_name
    assert len(owners) == 6
    assert all(splits[name] for name in ("train", "validation", "test"))


def test_invalid_ratios_are_rejected():
    rows = make_rows()
    with pytest.raises(ValueError, match="sum to 1.0"):
        split_dataset(rows, list(rows[0]), {"train": 0.6, "validation": 0.2, "test": 0.1})


def test_stratification_rejects_rare_labels():
    rows = make_rows(12)
    for index, row in enumerate(rows):
        row["target"] = "rare" if index == 0 else "common"
    with pytest.raises(ValueError, match="at least 3 rows"):
        split_dataset(rows, list(rows[0]), DEFAULT_RATIOS, stratify_by="target")


def test_group_mode_rejects_blank_group_ids():
    rows = make_rows()
    rows[0]["customer_id"] = ""
    with pytest.raises(ValueError, match="blank value"):
        split_dataset(rows, list(rows[0]), DEFAULT_RATIOS, group_column="customer_id")


def test_group_and_stratification_modes_are_mutually_exclusive():
    rows = make_rows()
    with pytest.raises(ValueError, match="either --stratify-by or --group-column"):
        split_dataset(rows, list(rows[0]), DEFAULT_RATIOS, stratify_by="returned", group_column="customer_id")