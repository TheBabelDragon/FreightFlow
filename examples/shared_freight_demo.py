#!/usr/bin/env python3
"""FreightFlow v0.2 \u2014 shared-load reference demo (Esri-ready).

3 distributors \u2192 1 shared truck \u2192 validated \u2192 settled \u2192 balanced ledger.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from decimal import Decimal

from data.reference_scenario import (
    SHIPMENTS,
    VEHICLE,
    CONTRACTS,
    NETWORK_ROUTE,
    TOTAL_TRANSPORT_COST,
    DISTRIBUTOR_NAMES,
)
from freightflow.domain.allocation import AllocationPolicy
from freightflow.allocation.allocation_engine import AllocationEngine
from freightflow.adapters.multiflow import MultiFlowAdapter
from freightflow.adapters.arcgis import ArcGISAdapter
from freightflow.ledger.ledger import Ledger
from freightflow.ledger.settlement import SettlementService


def main() -> int:
    print("FREIGHTFLOW SHARED LOAD")
    print("=" * 40)

    arcgis = ArcGISAdapter()
    route = NETWORK_ROUTE
    assert route.source == "fixture"
    print(f"Route:       {route.origin} \u2192 {route.destination}")
    print(f"  (network source: {route.source}, id: {route.id})")
    print(f"  distance: {route.distance} mi, travel: {route.travel_time_hours} h")

    vehicle = VEHICLE
    shipments = list(SHIPMENTS)
    total_cost = TOTAL_TRANSPORT_COST
    policy = AllocationPolicy.WEIGHT

    print(f"Vehicle:     {vehicle.id}")
    print(f"Capacity:    {vehicle.max_volume} pallets")
    total_vol = sum(s.volume for s in shipments)
    util = (total_vol / vehicle.max_volume * 100).quantize(Decimal("1"))
    print(f"Utilization: {util}%")
    print()

    mf = MultiFlowAdapter()
    report = mf.validate(shipments, vehicle, CONTRACTS)
    if not report.valid:
        fail = report.first_failure()
        print("MultiFlow validation: REJECTED")
        print(f"  Code: {fail.code if fail else 'UNKNOWN'}")
        print(f"  {fail.message if fail else ''}")
        return 1

    engine = AllocationEngine()
    ok, allocations, report = engine.propose_and_validate(
        shipments=shipments,
        vehicle=vehicle,
        contracts=CONTRACTS,
        total_cost=total_cost,
        policy=policy,
        route_id=route.id,
    )
    assert ok and allocations

    for a in allocations:
        s = next(x for x in shipments if x.id == a.shipment_id)
        name = DISTRIBUTOR_NAMES.get(s.distributor_id, s.distributor_id)
        print(f"{name:<12} {a.allocated_volume:>2} pallets     ${a.cost_share}")
    print(f"{'Transport cost:':<24} ${total_cost}")
    print()
    print(f"MultiFlow validation:  VALID")
    print(f"Allocation policy:     {policy.value}")

    ledger = Ledger()
    svc = SettlementService(ledger)
    settlement = svc.settle(
        allocations=allocations,
        shipments=shipments,
        vehicle_id=vehicle.id,
        total_cost=total_cost,
        route_id=route.id,
    )
    recon = settlement.reconciliation()
    print(f"Settlement:            {settlement.status.value}")
    print(f"Ledger:                {'BALANCED' if ledger.is_balanced(settlement.transaction_id) else 'UNBALANCED'}")
    print(f"Settlement ID:         {settlement.id}")
    print(f"Transaction ID:        {settlement.transaction_id}")
    print(f"Reconciliation:        sum={recon['sum_of_shares']} balanced={recon['balanced']}")
    print()

    expl = svc.explain(
        settlement=settlement,
        participant_id="D-BABEL",
        shipments=shipments,
        allocations=allocations,
        route_origin=route.origin,
        route_destination=route.destination,
        participant_name="Babel Supply",
    )
    print("--- Why does Babel owe $300? ---")
    for line in expl.to_lines():
        print(f"  {line}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
