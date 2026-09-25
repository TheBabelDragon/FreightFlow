#!/usr/bin/env python3
"""End-to-end shared freight demo.

Three distributors, one truck, Dallas → Phoenix, full utilization,
deterministic cost allocation, ledger settlement, and a rejection case.
"""

from __future__ import annotations

from decimal import Decimal

from freightflow.domain.distributor import Distributor
from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.domain.contract import Contract
from freightflow.domain.allocation import AllocationPolicy
from freightflow.allocation.allocation_engine import AllocationEngine
from freightflow.ledger.ledger import Ledger
from freightflow.ledger.settlement import SettlementService
from freightflow.ledger.audit import AuditTrail
from freightflow.adapters.arcgis import ArcGISAdapter


def main() -> None:
    print("=" * 60)
    print("FREIGHTFLOW SHARED-LOAD DEMO")
    print("=" * 60)

    # --- Participants ---
    acme = Distributor(id="D-ACME", name="ACME Distribution")
    babel = Distributor(id="D-BABEL", name="Babel Supply")
    desert = Distributor(id="D-DESERT", name="Desert Wholesale")

    # --- Shipments (Dallas → Phoenix) ---
    shipments = [
        Shipment(
            id="S-ACME-001",
            distributor_id=acme.id,
            origin="Dallas",
            destination="Phoenix",
            weight=Decimal("800"),
            volume=Decimal("8"),  # pallets
        ),
        Shipment(
            id="S-BABEL-004",
            distributor_id=babel.id,
            origin="Dallas",
            destination="Phoenix",
            weight=Decimal("500"),
            volume=Decimal("5"),
        ),
        Shipment(
            id="S-DESERT-007",
            distributor_id=desert.id,
            origin="Dallas",
            destination="Phoenix",
            weight=Decimal("700"),
            volume=Decimal("7"),
        ),
    ]

    # --- Vehicle ---
    truck = Vehicle(
        id="Truck-17",
        carrier_id="TruckCo-17",
        max_weight=Decimal("10000"),
        max_volume=Decimal("20"),  # 20 pallets
        origin="Dallas",
    )

    total_cost = Decimal("1200.00")

    # --- Route (ArcGIS stub) ---
    arcgis = ArcGISAdapter()
    route = arcgis.route_from_network(
        origin="Dallas",
        destination="Phoenix",
        distance=Decimal("887"),
        travel_time_hours=Decimal("13.5"),
    )

    # --- Happy path: shared load ---
    engine = AllocationEngine()
    ok, allocations, reason = engine.propose_and_validate(
        shipments=shipments,
        vehicle=truck,
        total_cost=total_cost,
        policy=AllocationPolicy.WEIGHT_PROPORTIONAL,
        route_id=route.id,
    )

    if not ok:
        print(f"REJECTED: {reason}")
        return

    print("\n┌─────────────────────────────────────┐")
    print("│ SHARED FREIGHT ALLOCATION           │")
    print("├─────────────────────────────────────┤")
    print(f"│ Route       {route.origin} → {route.destination}")
    print(f"│ Vehicle     {truck.id}")
    print(f"│ Capacity    {truck.max_volume} pallets")
    print(f"│ Utilization 100%")
    print("│                                     │")
    for a in allocations:
        s = next(x for x in shipments if x.id == a.shipment_id)
        name = {"D-ACME": "ACME", "D-BABEL": "Babel", "D-DESERT": "Desert"}[s.distributor_id]
        print(f"│ {name:<14} {a.allocated_volume:>2} pallets   ${a.cost_share}")
    print("│                                     │")
    print(f"│ Total                       ${total_cost}")
    print("└─────────────────────────────────────┘")
    print("\nVALIDATED")

    # --- Settle ---
    ledger = Ledger()
    settlement_svc = SettlementService(ledger)
    settlement = settlement_svc.settle(
        allocations=allocations,
        shipments=shipments,
        vehicle_id=truck.id,
        total_cost=total_cost,
    )
    print("SETTLED")
    print(f"  Settlement ID: {settlement.id}")
    print(f"  Policy:        {settlement.policy}")

    # --- Audit ---
    audit = AuditTrail(ledger)
    print("\n--- Audit: Why does Babel owe $300? ---")
    for line in audit.explain("D-BABEL"):
        print(f"  {line}")

    # --- Rejection demo: exclusive carrier ---
    print("\n" + "=" * 60)
    print("CONFLICT DEMO: exclusive carrier requirement")
    print("=" * 60)

    exclusive_contract = Contract(
        id="B-119",
        distributor_id=babel.id,
        carrier_id="C-22",
        exclusive_carrier=True,
    )

    ok2, _, reason2 = engine.propose_and_validate(
        shipments=shipments,
        vehicle=truck,
        contracts={babel.id: exclusive_contract},
        total_cost=total_cost,
        policy=AllocationPolicy.WEIGHT_PROPORTIONAL,
        route_id=route.id,
    )

    if not ok2:
        print(f"\nAllocation REJECTED.")
        print(f"Reason: {reason2}")
        print("Affected participant: Babel Supply")
        print("Constraint: CONTRACT-CARRIER-EXCLUSIVITY")
    else:
        print("Unexpected: should have been rejected")


if __name__ == "__main__":
    main()
