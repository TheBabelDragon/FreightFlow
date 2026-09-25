"""Contract domain model."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class Contract(BaseModel):
    """Commercial contract between distributor and carrier(s)."""

    model_config = {"frozen": True}

    id: str
    distributor_id: str
    carrier_id: str
    permitted_carriers: list[str] = Field(
        default_factory=list,
        description="If non-empty, only these carriers are allowed",
    )
    origin_constraints: list[str] = Field(default_factory=list)
    destination_constraints: list[str] = Field(default_factory=list)
    service_requirements: list[str] = Field(default_factory=list)
    rate_model: dict[str, Any] = Field(default_factory=dict)
    capacity_commitment: Decimal | None = None
    penalties: dict[str, Any] = Field(default_factory=dict)
    exclusive_carrier: bool = False
    shareable: bool = True

    def allows_carrier(self, carrier_id: str) -> bool:
        if self.exclusive_carrier and self.carrier_id != carrier_id:
            return False
        if self.permitted_carriers and carrier_id not in self.permitted_carriers:
            return False
        return True
