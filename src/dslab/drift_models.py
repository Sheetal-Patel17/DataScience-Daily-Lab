from dataclasses import asdict, dataclass, field


@dataclass
class DriftFinding:
    category: str
    column: str
    severity: str
    baseline_value: str
    current_value: str
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DriftReport:
    baseline_file: str
    current_file: str
    baseline_rows: int
    current_rows: int
    findings: list[DriftFinding] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.findings)

    def to_dict(self) -> dict:
        severities = ("high", "medium", "low")
        return {
            "baseline_file": self.baseline_file,
            "current_file": self.current_file,
            "baseline_rows": self.baseline_rows,
            "current_rows": self.current_rows,
            "has_drift": self.has_drift,
            "summary": {
                "findings_count": len(self.findings),
                **{
                    f"{severity}_count": sum(
                        item.severity == severity for item in self.findings
                    )
                    for severity in severities
                },
            },
            "findings": [item.to_dict() for item in self.findings],
        }
