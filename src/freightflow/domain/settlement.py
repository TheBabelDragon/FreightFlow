"""Settlement domain model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field

from .allocation import AllocationPolicy


class SettlementStatus(str, Enum):
    PENDING = "PENDING"
    POSTED = "POSTED"
    REVERSED = "REVERSED"


class Settlement(BaseModel):
    """Auditable financial settlement for a shared allocation."""

    id: str
    allocation_ids: list[str]
    vehicle_id: str
    total_transport_cost: Decimal
    policy: AllocationPolicy
    participant_shares: dict[str, Decimal] = Field(
        ..., description="distributor_id → exact monetary amount"
    )
    currency: str = "USD"
    status: SettlementStatus = SettlementStatus.PENDING
    created_at: datetime | None = None
    explanation: str | None = None
