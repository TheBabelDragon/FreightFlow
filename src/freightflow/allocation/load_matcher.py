"""Shared-load discovery / matching."""

from __future__ import annotations

from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle


class LoadMatcher:
    """Find feasible sets of shipments that fit a vehicle."""

    def find_compatible(
        self,
        shipments: list[Shipment],
        vehicle: Vehicle,
    ) -> list[list[Shipment]]:
        """Return candidate co-load groups that fit capacity (greedy for v0.1)."""
        # v0.1: simple greedy by volume; MultiFlow will validate properly later
        sorted_s = sorted(shipments, key=lambda s: s.volume, reverse=True)
        groups: list[list[Shipment]] = []
        remaining = list(sorted_s)

        while remaining:
            group: list[Shipment] = []
            used_w = vehicle.max_weight * 0
            used_v = vehicle.max_volume * 0
            still = []
            for s in remaining:
                if not s.shareable and group:
                    still.append(s)
                    continue
                if used_w + s.weight <= vehicle.max_weight and used_v + s.volume <= vehicle.max_volume:
                    group.append(s)
                    used_w += s.weight
                    used_v += s.volume
                else:
                    still.append(s)
            if group:
                groups.append(group)
            remaining = still
            if not group:
                break

        return groups
