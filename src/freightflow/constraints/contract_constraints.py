"""Contract constraint validators."""

from __future__ import annotations

from freightflow.domain.contract import Contract
from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle


class ContractValidator:
    """Shipment must satisfy contractual carrier / service restrictions."""

    def validate(
        self,
        shipment: Shipment,
        vehicle: Vehicle,
        contract: Contract | None,
    ) -> tuple[bool, str | None]:
        if contract is None:
            return True, None

        if contract.exclusive_carrier and contract.carrier_id != vehicle.carrier_id:
            return False, (
                f"CONTRACT-CARRIER-EXCLUSIVITY: shipment {shipment.id} requires "
                f"contracted carrier {contract.carrier_id}; proposed {vehicle.carrier_id}"
            )

        if contract.origin_constraints and shipment.origin not in contract.origin_constraints:
            return False, (
                f"CONTRACT-ORIGIN: origin {shipment.origin} not in "
                f"{contract.origin_constraints}"
            )

        if (
            contract.destination_constraints
            and shipment.destination not in contract.destination_constraints
        ):
            return False, (
                f"CONTRACT-DESTINATION: destination {shipment.destination} not in "
                f"{contract.destination_constraints}"
            )

        return True, None
