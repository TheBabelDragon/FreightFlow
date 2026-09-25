"""Network route model — ArcGIS integration boundary.

NetworkRoute is the stable internal representation of a physical route.
ArcGIS-derived data enters the system by mapping into this object.
Fixture/demo data uses the same shape so tests never need live ArcGIS.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class NetworkRoute(BaseModel):
    """Normalized route from network/geography layer (ArcGIS or fixture)."""

    model_config = {"frozen": True}

    id: str
    origin: str
    destination: str
    distance: Decimal | None = None
    travel_time_hours: Decimal | None = None
    geometry: Any | None = Field(
        default=None,
        description="Optional geometry (GeoJSON-like); not required for allocation",
    )
    network_metadata: dict[str, Any] = Field(default_factory=dict)
    source: str = Field(
        default="fixture",
        description="'fixture' for demo data; 'arcgis' when from live service",
    )
