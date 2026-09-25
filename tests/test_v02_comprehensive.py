"""FreightFlow v0.2 comprehensive tests \u2014 Esri demonstrator acceptance."""

from __future__ import annotations

from decimal import Decimal
from datetime import datetime, timezone

import pytest

from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.domain.contract import Contract
from freightflow.domain.allocation import AllocationPolicy
from freightflow.domain.settlement import SettlementStatus
from freightflow.domain.validation import ValidationResult
from freightflow.allocation.cost_allocator import CostAllocator
from freightflow.allocation.allocation_engine import AllocationEngine
from freightflow.constraints.capacity_constraints import CapacityValidator
from freightflow.constraints.contract_constraints import ContractValidator
from freightflow.constraints.allocation_constraints import AllocationValidator
from freightflow.constraints.delivery_constraints import DeliveryWindowValidator
from freightflow.ledger.ledger import Ledger
from freightflow.ledger.settlement import SettlementService
from freightflow.adapters.multiflow import MultiFlowAdapter
from freightflow.adapters.arcgis import ArcGISAdapter
from freightflow.domain.network import NetworkRoute


def _ref_shipments() -> list[Shipment]:
    return [
        Shipment(id="S-A", distributor_id="ACME", origin="Dallas", destination="Phoenix",
                 weight=Decimal("800"), volume=Decimal("8")),
        Shipment(id="S-B", distributor_id="Babel", origin="Dallas", destination="Phoenix",
                 weight=Decimal("500"), volume=Decimal("5")),
        Shipment(id="S-C", distributor_id="Desert", origin="Dallas", destination="Phoenix",
                 weight=Decimal("700"), volume=Decimal("7")),
    ]


def _truck() -> Vehicle:
    return Vehicle(id="Truck-17", carrier_id="TruckCo-17",
                   max_weight=Decimal("10000"), max_volume=Decimal("20"), origin="Dallas")


def test_reference_shared_load():
    engine = AllocationEngine()
    ok, allocs, report = engine.propose_and_validate(
        _ref_shipments(), _truck(), total_cost=Decimal("1200"), policy=AllocationPolicy.WEIGHT
    )
    assert ok and report.valid
    assert len(allocs) == 3
    by_dist = {}
    for a in allocs:
        s = next(x for x in _ref_shipments() if x.id == a.shipment_id)
        by_dist[s.distributor_id] = a.cost_share
    assert by_dist["ACME"] == Decimal("480.00")
    assert by_dist["Babel"] == Decimal("300.00")
    assert by_dist["Desert"] == Decimal("420.00")
    assert sum(by_dist.values()) == Decimal("1200.00")


def test_weight_cost_allocation():
    shares = CostAllocator().allocate(_ref_shipments(), Decimal("1200"), AllocationPolicy.WEIGHT)
    assert shares["ACME"] == Decimal("480.00")
    assert shares["Babel"] == Decimal("300.00")
    assert shares["Desert"] == Decimal("420.00")
    assert sum(shares.values()) == Decimal("1200")


def test_volume_cost_allocation():
    shares = CostAllocator().allocate(_ref_shipments(), Decimal("1200"), AllocationPolicy.VOLUME)
    assert shares["ACME"] == Decimal("480.00")
    assert shares["Babel"] == Decimal("300.00")
    assert shares["Desert"] == Decimal("420.00")


def test_weighted_composite_allocation():
    shares = CostAllocator().allocate(
        _ref_shipments(), Decimal("1200"), AllocationPolicy.WEIGHTED_COMPOSITE,
        weight_factor=Decimal("1"), volume_factor=Decimal("0"),
    )
    assert sum(shares.values()) == Decimal("1200")


def test_rounding_reconciliation():
    s = [
        Shipment(id="1", distributor_id="A", origin="X", destination="Y", weight=Decimal("1"), volume=Decimal("1")),
        Shipment(id="2", distributor_id="B", origin="X", destination="Y", weight=Decimal("1"), volume=Decimal("1")),
        Shipment(id="3", distributor_id="C", origin="X", destination="Y", weight=Decimal("1"), volume=Decimal("1")),
    ]
    shares = CostAllocator().allocate(s, Decimal("10.00"), AllocationPolicy.WEIGHT)
    assert sum(shares.values()) == Decimal("10.00")


def test_ledger_balances():
    engine = AllocationEngine()
    ok, allocs, _ = engine.propose_and_validate(
        _ref_shipments(), _truck(), total_cost=Decimal("1200"), policy=AllocationPolicy.WEIGHT
    )
    assert ok
    ledger = Ledger()
    settlement = SettlementService(ledger).settle(allocs, _ref_shipments(), "Truck-17", Decimal("1200"))
    assert ledger.is_balanced(settlement.transaction_id)
    assert settlement.reconciliation()["balanced"] is True
    assert ledger.balance("ACME") == Decimal("480.00")
    assert ledger.balance("Babel") == Decimal("300.00")
    assert ledger.balance("Desert") == Decimal("420.00")


def test_settlement_explanation():
    engine = AllocationEngine()
    ok, allocs, _ = engine.propose_and_validate(
        _ref_shipments(), _truck(), total_cost=Decimal("1200"), policy=AllocationPolicy.WEIGHT
    )
    ledger = Ledger()
    svc = SettlementService(ledger)
    settlement = svc.settle(allocs, _ref_shipments(), "Truck-17", Decimal("1200"))
    expl = svc.explain(
        settlement, "Babel", _ref_shipments(), allocs,
        route_origin="Dallas", route_destination="Phoenix", participant_name="Babel Supply",
    )
    assert expl.amount == Decimal("300.00")
    assert expl.policy == AllocationPolicy.WEIGHT
    lines = expl.to_lines()
    assert any("300" in ln for ln in lines)
    assert any("WEIGHT" in ln for ln in lines)


def test_capacity_rejection():
    truck = Vehicle(id="T", carrier_id="C", max_weight=Decimal("100"), max_volume=Decimal("5"))
    result = CapacityValidator().validate(_ref_shipments(), truck)
    assert not result.valid
    assert result.code == "CAPACITY-OVERFLOW"


def test_contract_rejection():
    s = Shipment(id="S-B", distributor_id="Babel", origin="D", destination="P",
                 weight=Decimal("5"), volume=Decimal("5"))
    v = Vehicle(id="T17", carrier_id="TruckCo-17", max_weight=Decimal("1000"), max_volume=Decimal("20"))
    c = Contract(id="B-119", distributor_id="Babel", carrier_id="C-22", exclusive_carrier=True)
    result = ContractValidator().validate(s, v, c)
    assert not result.valid
    assert result.code == "CONTRACT-CARRIER-EXCLUSIVITY"
    assert "C-22" in result.message


def test_delivery_window_rejection():
    s = Shipment(
        id="S1", distributor_id="A", origin="D", destination="P",
        weight=Decimal("1"), volume=Decimal("1"),
        latest_delivery=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    v = Vehicle(id="T", carrier_id="C", max_weight=Decimal("100"), max_volume=Decimal("10"))
    result = DeliveryWindowValidator().validate(
        s, v, planned_delivery=datetime(2026, 6, 1, tzinfo=timezone.utc)
    )
    assert not result.valid
    assert result.code == "DELIVERY-WINDOW"


def test_nonshareable_rejection():
    s = [
        Shipment(id="S1", distributor_id="A", origin="D", destination="P",
                 weight=Decimal("1"), volume=Decimal("1"), shareable=False),
        Shipment(id="S2", distributor_id="B", origin="D", destination="P",
                 weight=Decimal("1"), volume=Decimal("1"), shareable=True),
    ]
    result = AllocationValidator().validate_shareable(s)
    assert not result.valid
    assert result.code == "SHIPMENT-NOT-SHAREABLE"


def test_rejected_allocation_does_not_settle():
    contracts = {
        "Babel": Contract(id="B-119", distributor_id="Babel", carrier_id="C-22", exclusive_carrier=True),
    }
    engine = AllocationEngine()
    ok, allocs, report = engine.propose_and_validate(
        _ref_shipments(), _truck(), contracts=contracts, total_cost=Decimal("1200")
    )
    assert not ok
    assert allocs is None
    assert report.first_failure().code == "CONTRACT-CARRIER-EXCLUSIVITY"
    ledger = Ledger()
    assert len(ledger) == 0


def test_multiflow_validation():
    mf = MultiFlowAdapter()
    report = mf.validate(_ref_shipments(), _truck())
    assert report.valid
    contracts = {
        "Babel": Contract(id="B-119", distributor_id="Babel", carrier_id="C-22", exclusive_carrier=True),
    }
    report2 = mf.validate(_ref_shipments(), _truck(), contracts)
    assert not report2.valid
    assert report2.first_failure().code == "CONTRACT-CARRIER-EXCLUSIVITY"


def test_arcgis_fixture_adapter():
    adapter = ArcGISAdapter()
    route = adapter.from_network_result(
        {
            "route_id": "RTE-DAL-PHX",
            "origin": "Dallas",
            "destination": "Phoenix",
            "distance": "887",
            "travel_time_hours": "13.5",
            "network_metadata": {"corridor": "I-20"},
        },
        source="fixture",
    )
    assert isinstance(route, NetworkRoute)
    assert route.source == "fixture"
    assert route.distance == Decimal("887")
    viz = adapter.to_visualization(route)
    assert viz["origin"] == "Dallas"
    assert viz["source"] == "fixture"


def test_end_to_end_happy_path():
    engine = AllocationEngine()
    ok, allocs, report = engine.propose_and_validate(
        _ref_shipments(), _truck(), total_cost=Decimal("1200"), policy=AllocationPolicy.WEIGHT,
        route_id="RTE-DAL-PHX",
    )
    assert ok and report.valid
    ledger = Ledger()
    settlement = SettlementService(ledger).settle(
        allocs, _ref_shipments(), "Truck-17", Decimal("1200"), route_id="RTE-DAL-PHX"
    )
    assert settlement.status == SettlementStatus.POSTED
    assert ledger.is_balanced()
    assert sum(settlement.participant_shares.values()) == Decimal("1200.00")


def test_end_to_end_conflict_path():
    contracts = {
        "Babel": Contract(id="B-119", distributor_id="Babel", carrier_id="C-22", exclusive_carrier=True),
    }
    engine = AllocationEngine()
    ok, allocs, report = engine.propose_and_validate(
        _ref_shipments(), _truck(), contracts=contracts, total_cost=Decimal("1200")
    )
    assert not ok
    assert allocs is None
    fail = report.first_failure()
    assert fail.code == "CONTRACT-CARRIER-EXCLUSIVITY"


def test_determinism_replay():
    engine = AllocationEngine()
    r1 = engine.propose_and_validate(
        _ref_shipments(), _truck(), total_cost=Decimal("1200"), policy=AllocationPolicy.WEIGHT
    )
    r2 = engine.propose_and_validate(
        _ref_shipments(), _truck(), total_cost=Decimal("1200"), policy=AllocationPolicy.WEIGHT
    )
    assert r1[0] and r2[0]
    shares1 = sorted(a.cost_share for a in r1[1])
    shares2 = sorted(a.cost_share for a in r2[1])
    assert shares1 == shares2


def test_no_float_money():
    with pytest.raises(TypeError):
        CostAllocator().allocate(_ref_shipments(), 1200.0, AllocationPolicy.WEIGHT)  # type: ignore[arg-type]


def test_validation_result_structure():
    r = ValidationResult.fail("CAPACITY-OVERFLOW", "too full", ["Truck-17"])
    assert r.valid is False
    assert r.code == "CAPACITY-OVERFLOW"
    assert "Truck-17" in r.affected_entities
