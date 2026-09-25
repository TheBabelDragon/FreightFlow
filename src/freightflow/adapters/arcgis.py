"""ArcGIS adapter \u2014 network / geography integration boundary.

Keep ArcGIS out of the core domain model.

Entry point for ArcGIS-derived data:
  ArcGIS service response (or fixture)
      \u2193
  ArcGISAdapter.from_network_result(...)
      \u2193
  NetworkRoute (stable internal object)
      \u2193
  FreightFlow allocation / settlement

v0.2 uses checked-in deterministic fixtures.
Live ArcGIS calls are NOT performed and NOT claimed.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from freightflow.domain.network import NetworkRoute


class ArcGISAdapter:
    """Consume normalized network results; export visualization payloads."""

    def from_network_result(
        self,
        data: dict[str, Any],
        *,
        source: str = "fixture",
    ) -> NetworkRoute:
        """Map a normalized network result into NetworkRoute."""
        route_id = data.get("route_id") or data.get("id") or "RTE-UNKNOWN"
        distance = data.get("distance")
        travel = data.get("travel_time_hours") or data.get("travel_time")
        return NetworkRoute(
            id=str(route_id),
            origin=str(data["origin"]),
            destination=str(data["destination"]),
            distance=Decimal(str(distance)) if distance is not None else None,
            travel_time_hours=Decimal(str(travel)) if travel is not None else None,
            geometry=data.get("geometry"),
            network_metadata=dict(data.get("network_metadata") or {}),
            source=source,
        )

    def route_from_fixture(
        self,
        origin: str,
        destination: str,
        *,
        distance: Decimal | None = None,
        travel_time_hours: Decimal | None = None,
        route_id: str | None = None,
        network_metadata: dict[str, Any] | None = None,
    ) -> NetworkRoute:
        """Build NetworkRoute from explicit fixture parameters (demo/tests)."""
        return NetworkRoute(
            id=route_id or f"RTE-{origin[:3].upper()}-{destination[:3].upper()}",
            origin=origin,
            destination=destination,
            distance=distance,
            travel_time_hours=travel_time_hours,
            network_metadata=network_metadata or {},
            source="fixture",
        )

    def to_visualization(
        self,
        route: NetworkRoute,
        allocations: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Prepare payload for ArcGIS map display."""
        return {
            "route_id": route.id,
            "origin": route.origin,
            "destination": route.destination,
            "distance": str(route.distance) if route.distance is not None else None,
            "travel_time_hours": (
                str(route.travel_time_hours) if route.travel_time_hours is not None else None
            ),
            "geometry": route.geometry,
            "source": route.source,
            "allocations": [
                a.id if hasattr(a, "id") else str(a) for a in (allocations or [])
            ],
        }
