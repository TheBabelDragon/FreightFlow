"""Deterministic cost allocation policies.

Never invent financial numbers. Policy is part of the settlement record.
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
        policy: AllocationPolicy = AllocationPolicy.WEIGHT_PROPORTIONAL,
        weight_factor: Decimal = Decimal("1"),
        volume_factor: Decimal = Decimal("0"),
        distance_factor: Decimal = Decimal("0"),
        distances: dict[str, Decimal] | None = None,
    ) -> dict[str, Decimal]:
        """Return distributor_id → exact monetary share."""
        if not shipments:
            return {}

        if policy == AllocationPolicy.WEIGHT_PROPORTIONAL:
            total = sum((s.weight for s in shipments), Decimal("0"))
            if total == 0:
                raise ValueError("Cannot allocate by weight when total weight is zero")
            shares = {
                s.distributor_id: (s.weight / total * total_cost).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                for s in shipments
            }

        elif policy == AllocationPolicy.VOLUME_PROPORTIONAL:
            total = sum((s.volume for s in shipments), Decimal("0"))
            if total == 0:
                raise ValueError("Cannot allocate by volume when total volume is zero")
            shares = {
                s.distributor_id: (s.volume / total * total_cost).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                for s in shipments
            }

        elif policy == AllocationPolicy.WEIGHTED_COMPOSITE:
            distances = distances or {}
            scores: dict[str, Decimal] = {}
            for s in shipments:
                dist = distances.get(s.id, Decimal("0"))
                scores[s.distributor_id] = (
                    s.weight * weight_factor
                    + s.volume * volume_factor
                    + dist * distance_factor
                )
            total_score = sum(scores.values(), Decimal("0"))
            if total_score == 0:
                raise ValueError("Composite score total is zero")
            shares = {
                did: (score / total_score * total_cost).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                for did, score in scores.items()
            }

        else:
            raise ValueError(f"Unknown policy: {policy}")

        # Fix rounding remainder on largest share so sum == total_cost
        current = sum(shares.values(), Decimal("0"))
        if current != total_cost and shares:
            largest = max(shares, key=shares.get)
            shares[largest] += total_cost - current

        return shares
