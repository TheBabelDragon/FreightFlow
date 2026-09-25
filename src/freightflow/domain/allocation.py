"""Allocation domain model — the central object."""

from __future__ import annotations

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class AllocationPolicy(str, Enum):
    WEIGHT_PROPORTIONAL = "WEIGHT_PROPORTIONAL"
    VOLUME_PROPORTIONAL = "VOLUME_PROPORTIONAL"
    WEIGHTED_COMPOSITE = "WEIGHTED_COMPOSITE"


class Allocation(BaseModel):
    """A validated assignment of shipment capacity to a vehicle/route."""

    id: str
    shipment_id: str
    vehicle_id: str
    route_id: str | None = None
    allocated_weight: Decimal
    allocated_volume: Decimal
    cost_share: Decimal = Field(..., description="Exact monetary share of transport cost")
    contract_basis: str | None = None
    policy: AllocationPolicy = AllocationPolicy.WEIGHT_PROPORTIONAL
