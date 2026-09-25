"""Allocation-level constraint validators."""

from __future__ import annotations

from freightflow.domain.shipment import Shipment


class AllocationValidator:
    """Exclusivity and shareability rules."""

    def validate_shareable(self, shipments: list[Shipment]) -> tuple[bool, str | None]:
        for s in shipments:
            if not s.shareable and len(shipments) > 1:
                return False, (
                    f"NON-SHAREABLE: shipment {s.id} cannot be co-loaded "
                    f"(shareable=False)"
                )
        return True, None
