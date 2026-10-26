from pathlib import Path

from dslab.scorecard_metrics import (
    count_duplicate_rows,
    count_invalid_rows,
    count_missing_cells,
    read_dataset,
)
from dslab.scorecard_models import QualityScorecard


def grade_score(score: float, grades: dict) -> str:
    if score >= grades["excellent"]:
        return "Excellent"
    if score >= grades["good"]:
        return "Good"
    if score >= grades["needs_improvement"]:
        return "Needs Improvement"
    return "Poor"


def build_scorecard(
    csv_path: str | Path,
    config: dict,
) -> QualityScorecard:
    columns, rows = read_dataset(csv_path)
    row_count = len(rows)
    total_cells = row_count * len(columns)
    missing = count_missing_cells(columns, rows)
    duplicates = count_duplicate_rows(rows)
    invalid = count_invalid_rows(
        rows,
        config.get("required_columns", []),
        config.get("numeric_ranges", {}),
    )

    completeness = (
        100.0 if total_cells == 0
        else 100.0 * (total_cells - missing) / total_cells
    )
    uniqueness = (
        100.0 if row_count == 0
        else 100.0 * (row_count - duplicates) / row_count
    )
    validity = (
        100.0 if row_count == 0
        else 100.0 * (row_count - invalid) / row_count
    )

    weights = config["weights"]
    weight_total = sum(weights.values())
    if weight_total <= 0:
        raise ValueError("Scoring weights must have a positive total.")
    if any(weight < 0 for weight in weights.values()):
        raise ValueError("Scoring weights cannot be negative.")

    score = (
        completeness * weights["completeness"]
        + uniqueness * weights["uniqueness"]
        + validity * weights["validity"]
    ) / weight_total
    score = round(max(0.0, min(100.0, score)), 2)

    recommendations = []
    if missing:
        recommendations.append(
            f"Investigate {missing} missing cell(s) across the dataset."
        )
    if duplicates:
        recommendations.append(
            f"Review and remove {duplicates} duplicate row(s) if appropriate."
        )
    if invalid:
        recommendations.append(
            f"Review {invalid} row(s) with missing required fields "
            "or out-of-range values."
        )
    if not recommendations:
        recommendations.append("No issues found by the configured checks.")

    return QualityScorecard(
        str(csv_path),
        row_count,
        len(columns),
        missing,
        total_cells,
        duplicates,
        invalid,
        round(completeness, 2),
        round(uniqueness, 2),
        round(validity, 2),
        score,
        grade_score(score, config["grades"]),
        recommendations,
    )
