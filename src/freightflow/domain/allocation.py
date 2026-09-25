"""Allocation domain model — the central object."""

from __future__ import annotations

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class AllocationPolicy(str, Enum):
    """Explicit cost-allocation policy. Recorded on every settlement."""

    WEIGHT = "WEIGHT"
    VOLUME = "VOLUME"
    WEIGHTED_COMPOSITE = "WEIGHTED_COMPOSITE"


class Allocation(BaseModel):
    """A validated assignment of shipment capacity to a vehicle/route."""

    model_config = {"frozen": True}

    id: str
    shipment_id: str
    vehicle_id: str
    route_id: str | None = None
    allocated_weight: Decimal
    allocated_volume: Decimal
    cost_share: Decimal = Field(..., description="Exact monetary share; Decimal only")
    currency: str = "USD"
    contract_basis: str | None = None
    policy: AllocationPolicy = AllocationPolicy.WEIGHT
    share_numerator: Decimal | None = None
    share_denominator: Decimal | None = None

    @field_validator("cost_share", "allocated_weight", "allocated_volume", mode="before")
    @classmethod
    def _no_float(cls, v: object) -> Decimal:
        if isinstance(v, float):
            raise TypeError("Financial/quantity fields must not be float")
        return Decimal(str(v))
