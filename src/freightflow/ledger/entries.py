"""Ledger entry model."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from pydantic import BaseModel, Field


class LedgerEntry(BaseModel):
    """Single append-only accounting entry."""

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
