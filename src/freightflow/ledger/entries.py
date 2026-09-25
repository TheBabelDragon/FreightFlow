"""Ledger entry model."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class LedgerEntry(BaseModel):
    """Single append-only accounting entry."""

    model_config = {"frozen": True}

    entry_id: str = Field(default_factory=lambda: f"LE-{uuid4().hex[:12].upper()}")
    transaction_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    participant: str
    account: str
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    currency: str = "USD"
    allocation_id: str | None = None
    explanation: str = ""

    @field_validator("debit", "credit", mode="before")
    @classmethod
    def _no_float(cls, v: object) -> Decimal:
        if isinstance(v, float):
            raise TypeError("Ledger amounts must not be float")
        return Decimal(str(v))
