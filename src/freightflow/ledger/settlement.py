"""Settlement posting into the ledger.

Rejected allocations must never call settle \u2014 no financial entries on rejection.
"""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from freightflow.domain.allocation import Allocation, AllocationPolicy
from freightflow.domain.settlement import Settlement, SettlementStatus, SettlementExplanation
from freightflow.domain.shipment import Shipment
from freightflow.ledger.entries import LedgerEntry
from freightflow.ledger.ledger import Ledger


class SettlementService:
    """Create settlement and post balanced ledger entries."""

    def __init__(self, ledger: Ledger) -> None:
        self.ledger = ledger

    def settle(
        self,
        allocations: list[Allocation],
        shipments: list[Shipment],
        vehicle_id: str,
        total_cost: Decimal,
        currency: str = "USD",
        route_id: str | None = None,
        distributor_names: dict[str, str] | None = None,
    ) -> Settlement:
        if not allocations:
            raise ValueError("Cannot settle empty allocation list")

        shipment_map = {s.id: s for s in shipments}
        shares: dict[str, Decimal] = {}
        for a in allocations:
            s = shipment_map[a.shipment_id]
            shares[s.distributor_id] = shares.get(s.distributor_id, Decimal("0")) + a.cost_share

        policy = allocations[0].policy
        txn_id = f"TXN-{uuid4().hex[:10].upper()}"
        settlement_id = f"SET-{uuid4().hex[:8].upper()}"

        settlement = Settlement(
            id=settlement_id,
            allocation_ids=[a.id for a in allocations],
            vehicle_id=vehicle_id,
            route_id=route_id,
            total_transport_cost=total_cost,
            policy=policy,
            participant_shares=shares,
            currency=currency,
            status=SettlementStatus.POSTED,
            transaction_id=txn_id,
        )

        self.ledger.append(
            LedgerEntry(
                transaction_id=txn_id,
                participant="CARRIER",
                account="freight_receivable",
                credit=total_cost,
                currency=currency,
                explanation=f"Transport revenue for {vehicle_id}",
            )
        )

        for a in allocations:
            s = shipment_map[a.shipment_id]
            self.ledger.append(
                LedgerEntry(
                    transaction_id=txn_id,
                    participant=s.distributor_id,
                    account="freight_payable",
                    debit=a.cost_share,
                    currency=currency,
                    allocation_id=a.id,
                    explanation=(
                        f"Share of {vehicle_id} | shipment={a.shipment_id} | "
                        f"policy={a.policy.value} | weight={a.allocated_weight} | "
                        f"volume={a.allocated_volume}"
                    ),
                )
            )

        assert self.ledger.is_balanced(txn_id), "Ledger must balance after settlement"
        return settlement

    def explain(
        self,
        settlement: Settlement,
        participant_id: str,
        shipments: list[Shipment],
        allocations: list[Allocation],
        route_origin: str | None = None,
        route_destination: str | None = None,
        participant_name: str | None = None,
    ) -> SettlementExplanation:
        """Build structured explanation from facts only."""
        amount = settlement.participant_shares.get(participant_id, Decimal("0"))
        shipment_map = {s.id: s for s in shipments}
        alloc = next(
            (
                a
                for a in allocations
                if shipment_map[a.shipment_id].distributor_id == participant_id
            ),
            None,
        )

        total_qty = alloc.share_denominator if alloc else None
        alloc_qty = alloc.share_numerator if alloc else None
        pct = None
        if alloc_qty is not None and total_qty and total_qty != 0:
            pct = (alloc_qty / total_qty * Decimal("100")).quantize(Decimal("1"))

        return SettlementExplanation(
            participant_id=participant_id,
            participant_name=participant_name,
            amount=amount,
            currency=settlement.currency,
            contract_id=alloc.contract_basis if alloc else None,
            shipment_id=alloc.shipment_id if alloc else None,
            vehicle_id=settlement.vehicle_id,
            route_origin=route_origin,
            route_destination=route_destination,
            allocated_quantity=alloc_qty,
            total_quantity=total_qty,
            share_percent=pct,
            policy=settlement.policy,
            transport_cost=settlement.total_transport_cost,
            allocation_id=alloc.id if alloc else None,
            settlement_id=settlement.id,
        )
