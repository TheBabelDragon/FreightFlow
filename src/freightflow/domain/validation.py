"""Structured validation results with stable machine-readable codes."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """Single constraint check outcome. Not a bare boolean."""

    model_config = {"frozen": True}

    valid: bool
    code: str | None = None
    message: str | None = None
    affected_entities: list[str] = Field(default_factory=list)

    @classmethod
    def ok(cls) -> ValidationResult:
        return cls(valid=True)

    @classmethod
    def fail(
        cls,
        code: str,
        message: str,
        affected_entities: list[str] | None = None,
    ) -> ValidationResult:
        return cls(
            valid=False,
            code=code,
            message=message,
            affected_entities=affected_entities or [],
        )


class ValidationReport(BaseModel):
    """Aggregated results from multiple validators."""

    model_config = {"frozen": True}

    results: list[ValidationResult] = Field(default_factory=list)

    @property
    def valid(self) -> bool:
        return all(r.valid for r in self.results)

    @property
    def failures(self) -> list[ValidationResult]:
        return [r for r in self.results if not r.valid]

    def first_failure(self) -> ValidationResult | None:
        for r in self.results:
            if not r.valid:
                return r
        return None

    def add(self, result: ValidationResult) -> ValidationReport:
        return ValidationReport(results=[*self.results, result])

    def merge(self, other: ValidationReport) -> ValidationReport:
        return ValidationReport(results=[*self.results, *other.results])
