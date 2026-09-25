"""Contract constraint validators."""

from __future__ import annotations

from freightflow.domain.contract import Contract
from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.domain.validation import ValidationResult


class ContractValidator:
    """Shipment must satisfy contractual carrier / service restrictions."""

    def validate(
        self,
        shipment: Shipment,
        vehicle: Vehicle,
        contract: Contract | None,
    ) -> ValidationResult:
        if contract is None:
            return ValidationResult.ok()

        if not contract.allows_carrier(vehicle.carrier_id):
            required = contract.carrier_id
            if contract.permitted_carriers:
                required = ", ".join(contract.permitted_carriers)
            return ValidationResult.fail(
                code="CONTRACT-CARRIER-EXCLUSIVITY",
                message=(
                    f"Shipment {shipment.id} requires carrier {required}; "
                    f"proposed carrier {vehicle.carrier_id}"
                ),
                affected_entities=[
                    shipment.id,
                    shipment.distributor_id,
                    contract.id,
                    vehicle.id,
                    vehicle.carrier_id,
                ],
            )

        if contract.origin_constraints and shipment.origin not in contract.origin_constraints:
            return ValidationResult.fail(
                code="CONTRACT-ORIGIN",
                message=(
                    f"Origin {shipment.origin} not in contract "
                    f"{contract.id} origins {contract.origin_constraints}"
                ),
                affected_entities=[shipment.id, contract.id],
            )

        if (
            contract.destination_constraints
            and shipment.destination not in contract.destination_constraints
        ):
            return ValidationResult.fail(
                code="CONTRACT-DESTINATION",
                message=(
                    f"Destination {shipment.destination} not in contract "
                    f"{contract.id} destinations {contract.destination_constraints}"
                ),
                affected_entities=[shipment.id, contract.id],
            )

        return ValidationResult.ok()
