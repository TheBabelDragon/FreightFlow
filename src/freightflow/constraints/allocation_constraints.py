"""Allocation-level constraint validators."""

from __future__ import annotations

from freightflow.domain.shipment import Shipment
from freightflow.domain.validation import ValidationResult


class AllocationValidator:
    """Exclusivity, shareability, and completeness rules."""

    def validate_shareable(self, shipments: list[Shipment]) -> ValidationResult:
        for s in shipments:
            if not s.shareable and len(shipments) > 1:
                return ValidationResult.fail(
                    code="SHIPMENT-NOT-SHAREABLE",
                    message=(
                        f"Shipment {s.id} cannot be co-loaded (shareable=False)"
                    ),
                    affected_entities=[s.id, s.distributor_id],
                )
        return ValidationResult.ok()

    def validate_completeness(
        self,
        shipments: list[Shipment],
        allocated_shipment_ids: set[str],
    ) -> ValidationResult:
        missing = [s.id for s in shipments if s.id not in allocated_shipment_ids]
        if missing:
            return ValidationResult.fail(
                code="ALLOCATION-INCOMPLETE",
                message=f"Shipments not allocated: {', '.join(missing)}",
                affected_entities=missing,
            )
        return ValidationResult.ok()
