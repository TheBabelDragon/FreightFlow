"""End-to-end 3-distributor demo test + rejection."""

from decimal import Decimal

from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.domain.contract import Contract
from freightflow.domain.allocation import AllocationPolicy
from freightflow.allocation.allocation_engine import AllocationEngine
from freightflow.ledger.ledger import Ledger
from freightflow.ledger.settlement import SettlementService


def test_happy_path_shared_load():
    shipments = [
        Shipment(id="S-A", distributor_id="ACME", origin="Dallas", destination="Phoenix", weight=Decimal("800"), volume=Decimal("8")),
        Shipment(id="S-B", distributor_id="Babel", origin="Dallas", destination="Phoenix", weight=Decimal("500"), volume=Decimal("5")),
        Shipment(id="S-C", distributor_id="Desert", origin="Dallas", destination="Phoenix", weight=Decimal("700"), volume=Decimal("7")),
    ]
    truck = Vehicle(id="Truck-17", carrier_id="TruckCo-17", max_weight=Decimal("10000"), max_volume=Decimal("20"))

    engine = AllocationEngine()
    ok, allocations, report = engine.propose_and_validate(
        shipments, truck, total_cost=Decimal("1200"), policy=AllocationPolicy.WEIGHT
    )
    assert ok is True
    assert report.valid
    assert len(allocations) == 3

    ledger = Ledger()
    settlement = SettlementService(ledger).settle(allocations, shipments, truck.id, Decimal("1200"))
    assert sum(settlement.participant_shares.values()) == Decimal("1200.00")
    assert ledger.is_balanced()


def test_rejection_exclusive_carrier():
    shipments = [
        Shipment(id="S-A", distributor_id="ACME", origin="Dallas", destination="Phoenix", weight=Decimal("800"), volume=Decimal("8")),
        Shipment(id="S-B", distributor_id="Babel", origin="Dallas", destination="Phoenix", weight=Decimal("500"), volume=Decimal("5")),
        Shipment(id="S-C", distributor_id="Desert", origin="Dallas", destination="Phoenix", weight=Decimal("700"), volume=Decimal("7")),
    ]
    truck = Vehicle(id="Truck-17", carrier_id="TruckCo-17", max_weight=Decimal("10000"), max_volume=Decimal("20"))
    contract = Contract(id="B-119", distributor_id="Babel", carrier_id="C-22", exclusive_carrier=True)

    engine = AllocationEngine()
    ok, allocations, report = engine.propose_and_validate(
        shipments,
        truck,
        contracts={"Babel": contract},
        total_cost=Decimal("1200"),
    )
    assert ok is False
    assert allocations is None
    assert report.first_failure().code == "CONTRACT-CARRIER-EXCLUSIVITY"
