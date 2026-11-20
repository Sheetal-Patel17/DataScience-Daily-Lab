from dataclasses import asdict, dataclass


@dataclass
class QualityScorecard:
    file_name: str
    row_count: int
    column_count: int
    missing_cells: int
    total_cells: int
    duplicate_rows: int
    invalid_rows: int
    completeness_score: float
    uniqueness_score: float
    validity_score: float
    overall_score: float
    grade: str
    recommendations: list[str]

    def to_dict(self) -> dict:
        return asdict(self)
