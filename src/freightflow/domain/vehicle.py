"""Vehicle domain model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class Vehicle(BaseModel):
    """A transport asset available for allocation."""

    id: str
    carrier_id: str
    max_weight: Decimal
    max_volume: Decimal
    available_from: datetime | None = None
    available_until: datetime | None = None
    origin: str | None = None
