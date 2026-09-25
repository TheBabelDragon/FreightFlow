"""Shipment domain model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class Shipment(BaseModel):
    """A unit of freight to be moved."""

    id: str
    distributor_id: str
    origin: str
    destination: str
    weight: Decimal = Field(..., description="Weight units (e.g. kg or lbs)")
    volume: Decimal = Field(..., description="Volume units (e.g. pallets or m³)")
    earliest_pickup: datetime | None = None
    latest_delivery: datetime | None = None
    required_service: str | None = None
    shareable: bool = True
