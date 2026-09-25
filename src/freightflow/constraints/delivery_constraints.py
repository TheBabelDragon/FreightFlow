"""Delivery / time-window constraint validators."""

from __future__ import annotations

from datetime import datetime

from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle


class DeliveryWindowValidator:
    """pickup >= earliest_pickup; delivery <= latest_delivery."""

    def validate(
        self,
        shipment: Shipment,
        vehicle: Vehicle,
        planned_pickup: datetime | None = None,
        planned_delivery: datetime | None = None,
    ) -> tuple[bool, str | None]:
        if shipment.earliest_pickup and planned_pickup:
            if planned_pickup < shipment.earliest_pickup:
                return False, (
                    f"TIME-PICKUP: planned pickup {planned_pickup} before "
                    f"earliest {shipment.earliest_pickup}"
                )

        if shipment.latest_delivery and planned_delivery:
            if planned_delivery > shipment.latest_delivery:
                return False, (
                    f"TIME-DELIVERY: planned delivery {planned_delivery} after "
                    f"latest {shipment.latest_delivery}"
                )

        if vehicle.available_from and planned_pickup:
            if planned_pickup < vehicle.available_from:
                return False, (
                    f"TIME-VEHICLE-AVAIL: planned pickup before vehicle available_from"
                )

        if vehicle.available_until and planned_delivery:
            if planned_delivery > vehicle.available_until:
                return False, (
                    f"TIME-VEHICLE-AVAIL: planned delivery after vehicle available_until"
                )

        return True, None
