"""Delivery / time-window constraint validators."""

from __future__ import annotations

from datetime import datetime

from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.domain.validation import ValidationResult


class DeliveryWindowValidator:
    """pickup >= earliest_pickup; delivery <= latest_delivery."""

    def validate(
        self,
        shipment: Shipment,
        vehicle: Vehicle,
        planned_pickup: datetime | None = None,
        planned_delivery: datetime | None = None,
    ) -> ValidationResult:
        if shipment.earliest_pickup and planned_pickup:
            if planned_pickup < shipment.earliest_pickup:
                return ValidationResult.fail(
                    code="DELIVERY-WINDOW",
                    message=(
                        f"Planned pickup {planned_pickup} before earliest "
                        f"{shipment.earliest_pickup} for {shipment.id}"
                    ),
                    affected_entities=[shipment.id, vehicle.id],
                )

        if shipment.latest_delivery and planned_delivery:
            if planned_delivery > shipment.latest_delivery:
                return ValidationResult.fail(
                    code="DELIVERY-WINDOW",
                    message=(
                        f"Planned delivery {planned_delivery} after latest "
                        f"{shipment.latest_delivery} for {shipment.id}"
                    ),
                    affected_entities=[shipment.id, vehicle.id],
                )

        if vehicle.available_from and planned_pickup:
            if planned_pickup < vehicle.available_from:
                return ValidationResult.fail(
                    code="DELIVERY-WINDOW",
                    message=f"Planned pickup before vehicle {vehicle.id} available_from",
                    affected_entities=[shipment.id, vehicle.id],
                )

        if vehicle.available_until and planned_delivery:
            if planned_delivery > vehicle.available_until:
                return ValidationResult.fail(
                    code="DELIVERY-WINDOW",
                    message=f"Planned delivery after vehicle {vehicle.id} available_until",
                    affected_entities=[shipment.id, vehicle.id],
                )

        return ValidationResult.ok()
