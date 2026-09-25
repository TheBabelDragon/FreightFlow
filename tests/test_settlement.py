"""Settlement and ledger tests."""

from decimal import Decimal

from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.domain.allocation import AllocationPolicy
from freightflow.allocation.allocation_engine import AllocationEngine
from freightflow.ledger.ledger import Ledger
from freightflow.ledger.settlement import SettlementService
from freightflow.ledger.audit import AuditTrail


def test_settlement_balances():
    shipments = [
        Shipment(id="S1", distributor_id="A", origin="D", destination="P", weight=Decimal("8"), volume=Decimal("8")),
        Shipment(id="S2", distributor_id="B", origin="D", destination="P", weight=Decimal("5"), volume=Decimal("5")),
        Shipment(id="S3", distributor_id="C", origin="D", destination="P", weight=Decimal("7"), volume=Decimal("7")),
    ]
    vehicle = Vehicle(id="T17", carrier_id="TC", max_weight=Decimal("10000"), max_volume=Decimal("20"))
    engine = AllocationEngine()
    ok, allocations, _ = engine.propose_and_validate(
        shipments, vehicle, total_cost=Decimal("1200"), policy=AllocationPolicy.WEIGHT_PROPORTIONAL
    )
    assert ok

    ledger = Ledger()
    svc = SettlementService(ledger)
    settlement = svc.settle(allocations, shipments, vehicle.id, Decimal("1200"))

    assert settlement.participant_shares["A"] == Decimal("480.00")
    assert settlement.participant_shares["B"] == Decimal("300.00")
    assert settlement.participant_shares["C"] == Decimal("420.00")

    assert ledger.balance("A") == 480.0
    assert ledger.balance("B") == 300.0
    assert ledger.balance("C") == 420.0

    audit = AuditTrail(ledger)
    lines = audit.explain("B")
    assert len(lines) == 1
    assert "300" in lines[0]
