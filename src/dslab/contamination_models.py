"""Data models for dataset contamination audits."""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    count: int
    examples: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class AuditResult:
    input_rows: int
    unique_rows: int
    duplicate_rows: int
    cross_file_matches: int
    suspicious_columns: tuple[str, ...]
    findings: tuple[Finding, ...]

    def to_dict(self) -> dict:
        return {
            "input_rows": self.input_rows,
            "unique_rows": self.unique_rows,
            "duplicate_rows": self.duplicate_rows,
            "cross_file_matches": self.cross_file_matches,
            "suspicious_columns": list(self.suspicious_columns),
            "findings": [item.to_dict() for item in self.findings],
        }
