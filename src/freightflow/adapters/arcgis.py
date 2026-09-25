"""ArcGIS adapter — network / geography only.

Keep ArcGIS out of the core domain model.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from freightflow.domain.route import Route


class ArcGISAdapter:
    """Fetch network info and (later) push visualization."""

    def route_from_network(
        self,
        origin: str,
        destination: str,
        distance: Decimal | None = None,
        travel_time_hours: Decimal | None = None,
        network_constraints: list[str] | None = None,
    ) -> Route:
        """Build a FreightFlow Route from ArcGIS-derived data (stub)."""
        return Route(
            id=f"RTE-{origin[:3].upper()}-{destination[:3].upper()}",
            origin=origin,
            destination=destination,
            distance=distance,
            travel_time_hours=travel_time_hours,
            network_constraints=network_constraints or [],
        )

    def to_visualization(self, route: Route, allocations: list[Any]) -> dict[str, Any]:
        """Prepare payload for ArcGIS map display (stub)."""
        return {
            "route_id": route.id,
            "origin": route.origin,
            "destination": route.destination,
            "distance": str(route.distance) if route.distance else None,
            "allocations": [getattr(a, "id", str(a)) for a in allocations],
        }
