"""Data structures used by the validation rules engine."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationIssue:
    row_number: int
    field: str
    rule: str
    message: str
    value: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "row_number": self.row_number,
            "field": self.field,
            "rule": self.rule,
            "message": self.message,
            "value": self.value,
        }


@dataclass
class ValidationReport:
    source: str
    total_rows: int
    issues: list[ValidationIssue]

    @property
    def invalid_rows(self) -> int:
        return len({issue.row_number for issue in self.issues})

    @property
    def valid_rows(self) -> int:
        return self.total_rows - self.invalid_rows

    @property
    def is_valid(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "summary": {
                "total_rows": self.total_rows,
                "valid_rows": self.valid_rows,
                "invalid_rows": self.invalid_rows,
                "issue_count": len(self.issues),
                "is_valid": self.is_valid,
            },
            "issues": [issue.to_dict() for issue in self.issues],
        }
