"""Settlement domain model and structured explanation."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from .allocation import AllocationPolicy


class SettlementStatus(str, Enum):
    PENDING = "PENDING"
    POSTED = "POSTED"
    REVERSED = "REVERSED"
    NOT_CREATED = "NOT_CREATED"


class Settlement(BaseModel):
    """Auditable financial settlement for a shared allocation."""

    model_config = {"frozen": True}

    id: str
    allocation_ids: list[str]
    vehicle_id: str
    route_id: str | None = None
    total_transport_cost: Decimal
    policy: AllocationPolicy
    participant_shares: dict[str, Decimal] = Field(
        ..., description="distributor_id \u2192 exact monetary amount"
    )
    currency: str = "USD"
    status: SettlementStatus = SettlementStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    transaction_id: str | None = None

    @field_validator("total_transport_cost", mode="before")
    @classmethod
    def _no_float_total(cls, v: object) -> Decimal:
        if isinstance(v, float):
            raise TypeError("total_transport_cost must not be float")
        return Decimal(str(v))

    def reconciliation(self) -> dict[str, Decimal | bool]:
        """Prove sum(shares) == total_transport_cost."""
        total_shares = sum(self.participant_shares.values(), Decimal("0"))
        return {
            "total_transport_cost": self.total_transport_cost,
            "sum_of_shares": total_shares,
            "balanced": total_shares == self.total_transport_cost,
            "difference": self.total_transport_cost - total_shares,
        }


class SettlementExplanation(BaseModel):
    """Structured answer: Why does participant X owe $Y?

    Built from facts only \u2014 never LLM-generated prose.
    """

    model_config = {"frozen": True}

    participant_id: str
    participant_name: str | None = None
    amount: Decimal
    currency: str = "USD"
    contract_id: str | None = None
    shipment_id: str | None = None
    vehicle_id: str | None = None
    route_origin: str | None = None
    route_destination: str | None = None
    allocated_quantity: Decimal | None = None
    total_quantity: Decimal | None = None
    share_percent: Decimal | None = None
    policy: AllocationPolicy | None = None
    transport_cost: Decimal | None = None
    allocation_id: str | None = None
    settlement_id: str | None = None

    def to_lines(self) -> list[str]:
        """Deterministic human-readable lines from structured fields."""
        lines = [
            f"Participant: {self.participant_name or self.participant_id}",
            f"Amount: {self.currency} {self.amount.quantize(Decimal('0.01'))}",
        ]
        if self.contract_id:
            lines.append(f"Contract: {self.contract_id}")
        if self.shipment_id:
            lines.append(f"Shipment: {self.shipment_id}")
        if self.vehicle_id:
            lines.append(f"Vehicle: {self.vehicle_id}")
        if self.route_origin and self.route_destination:
            lines.append(f"Route: {self.route_origin} \u2192 {self.route_destination}")
        if self.allocated_quantity is not None and self.total_quantity is not None:
            pct = f" = {self.share_percent}%" if self.share_percent is not None else ""
            lines.append(f"Allocation: {self.allocated_quantity} / {self.total_quantity}{pct}")
        if self.policy:
            lines.append(f"Policy: {self.policy.value}")
        if self.transport_cost is not None:
            lines.append(
                f"Transport cost: {self.currency} {self.transport_cost.quantize(Decimal('0.01'))}"
            )
        if self.allocation_id:
            lines.append(f"Validated allocation: {self.allocation_id}")
        if self.settlement_id:
            lines.append(f"Settlement: {self.settlement_id}")
        return lines
