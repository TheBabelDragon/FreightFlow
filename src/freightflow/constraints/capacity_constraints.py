"""Capacity constraint validators."""

from __future__ import annotations

from decimal import Decimal

from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.domain.validation import ValidationResult


class CapacityValidator:
    """Σ shipment_weight ≤ vehicle.max_weight; Σ shipment_volume ≤ vehicle.max_volume."""

    def validate(
        self,
        shipments: list[Shipment],
        vehicle: Vehicle,
    ) -> ValidationResult:
        total_weight = sum((s.weight for s in shipments), Decimal("0"))
        total_volume = sum((s.volume for s in shipments), Decimal("0"))
        ids = [s.id for s in shipments]

        if total_weight > vehicle.max_weight:
            return ValidationResult.fail(
                code="CAPACITY-OVERFLOW",
                message=(
                    f"Total weight {total_weight} exceeds vehicle max weight "
                    f"{vehicle.max_weight} on {vehicle.id}"
                ),
                affected_entities=[vehicle.id, *ids],
            )
        if total_volume > vehicle.max_volume:
            return ValidationResult.fail(
                code="CAPACITY-OVERFLOW",
                message=(
                    f"Total volume {total_volume} exceeds vehicle max volume "
                    f"{vehicle.max_volume} on {vehicle.id}"
                ),
                affected_entities=[vehicle.id, *ids],
            )
        return ValidationResult.ok()
