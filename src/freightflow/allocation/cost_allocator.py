"""Deterministic cost allocation policies.

Never invent financial numbers. Policy is part of the settlement record.
sum(shares) == total_cost always (remainder assigned deterministically).
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from freightflow.domain.allocation import AllocationPolicy
from freightflow.domain.shipment import Shipment


class CostAllocator:
    """Allocate total transport cost by explicit, deterministic bases."""

    def allocate(
        self,
        shipments: list[Shipment],
        total_cost: Decimal,
        policy: AllocationPolicy = AllocationPolicy.WEIGHT,
        weight_factor: Decimal = Decimal("1"),
        volume_factor: Decimal = Decimal("0"),
        distance_factor: Decimal = Decimal("0"),
        distances: dict[str, Decimal] | None = None,
    ) -> dict[str, Decimal]:
        """Return distributor_id \u2192 exact monetary share.

        Guarantees sum(shares) == total_cost. Remainder goes to the
        lexicographically first distributor among those with the largest
        pre-rounding share (deterministic tie-break).
        """
        if isinstance(total_cost, float):
            raise TypeError("total_cost must be Decimal, not float")
        total_cost = Decimal(str(total_cost))

        if not shipments:
            return {}

        if policy == AllocationPolicy.WEIGHT:
            bases = {s.distributor_id: s.weight for s in shipments}
        elif policy == AllocationPolicy.VOLUME:
            bases = {s.distributor_id: s.volume for s in shipments}
        elif policy == AllocationPolicy.WEIGHTED_COMPOSITE:
            distances = distances or {}
            bases = {}
            for s in shipments:
                dist = distances.get(s.id, Decimal("0"))
                bases[s.distributor_id] = (
                    s.weight * weight_factor
                    + s.volume * volume_factor
                    + dist * distance_factor
                )
        else:
            raise ValueError(f"Unknown policy: {policy}")

        total_base = sum(bases.values(), Decimal("0"))
        if total_base == 0:
            raise ValueError("Cannot allocate when total basis is zero")

        raw = {
            did: (base / total_base * total_cost)
            for did, base in bases.items()
        }
        shares = {
            did: amt.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            for did, amt in raw.items()
        }

        current = sum(shares.values(), Decimal("0"))
        remainder = total_cost - current
        if remainder != 0 and shares:
            max_raw = max(raw.values())
            candidates = sorted(did for did, r in raw.items() if r == max_raw)
            target = candidates[0]
            shares[target] = shares[target] + remainder

        assert sum(shares.values(), Decimal("0")) == total_cost
        return shares

    def share_fraction(
        self,
        shipment: Shipment,
        shipments: list[Shipment],
        policy: AllocationPolicy = AllocationPolicy.WEIGHT,
    ) -> tuple[Decimal, Decimal]:
        """Return (numerator, denominator) for display (e.g. 5, 20)."""
        if policy == AllocationPolicy.VOLUME:
            num = shipment.volume
            den = sum((s.volume for s in shipments), Decimal("0"))
        else:
            num = shipment.weight
            den = sum((s.weight for s in shipments), Decimal("0"))
        return num, den
