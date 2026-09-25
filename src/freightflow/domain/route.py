"""Route domain model."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class Route(BaseModel):
    """A physical path between origin and destination."""

    id: str
    origin: str
    destination: str
    distance: Decimal | None = None
    travel_time_hours: Decimal | None = None
    network_constraints: list[str] = Field(default_factory=list)
