"""Capacity constraint validators."""

from __future__ import annotations

from decimal import Decimal

from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle


class CapacityValidator:
    """Σ shipment_weight ≤ vehicle.max_weight; Σ shipment_volume ≤ vehicle.max_volume."""

    def validate(
        self,
        shipments: list[Shipment],
        vehicle: Vehicle,
    ) -> tuple[bool, str | None]:
        total_weight = sum((s.weight for s in shipments), Decimal("0"))
        total_volume = sum((s.volume for s in shipments), Decimal("0"))

        if total_weight > vehicle.max_weight:
            return False, (
                f"CAPACITY-WEIGHT: total weight {total_weight} exceeds "
                f"vehicle max {vehicle.max_weight}"
            )
        if total_volume > vehicle.max_volume:
            return False, (
                f"CAPACITY-VOLUME: total volume {total_volume} exceeds "
                f"vehicle max {vehicle.max_volume}"
            )
        return True, None
