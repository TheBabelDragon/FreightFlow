"""Settlement posting into the ledger."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from freightflow.domain.allocation import Allocation
from freightflow.domain.settlement import Settlement, SettlementStatus
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
    ) -> Settlement:
        shipment_map = {s.id: s for s in shipments}
        shares: dict[str, Decimal] = {}
        for a in allocations:
            s = shipment_map[a.shipment_id]
            shares[s.distributor_id] = shares.get(s.distributor_id, Decimal("0")) + a.cost_share

        policy = allocations[0].policy if allocations else None
        txn_id = f"TXN-{uuid4().hex[:10].upper()}"

        settlement = Settlement(
            id=f"SET-{uuid4().hex[:8].upper()}",
            allocation_ids=[a.id for a in allocations],
            vehicle_id=vehicle_id,
            total_transport_cost=total_cost,
            policy=policy,
            participant_shares=shares,
            currency=currency,
            status=SettlementStatus.POSTED,
            explanation=(
                f"Shared load on {vehicle_id}; policy={policy}; "
                f"total={total_cost} {currency}"
            ),
        )

        # Carrier credit (receivable)
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

        # Distributor debits
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
                        f"policy={a.policy} | weight={a.allocated_weight} | "
                        f"volume={a.allocated_volume}"
                    ),
                )
            )

        return settlement
