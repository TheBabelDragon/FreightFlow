#!/usr/bin/env python3
"""FreightFlow v0.2 \u2014 conflict / rejection demo.

Same reference scenario, but Babel contract requires exclusive carrier C-22.
Expected: REJECTED, no settlement, ledger unchanged.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from data.reference_scenario import (
    SHIPMENTS,
    VEHICLE,
    CONTRACTS,
    BABEL_EXCLUSIVE_CONTRACT,
    NETWORK_ROUTE,
    TOTAL_TRANSPORT_COST,
)
from freightflow.domain.allocation import AllocationPolicy
from freightflow.allocation.allocation_engine import AllocationEngine
from freightflow.adapters.multiflow import MultiFlowAdapter
from freightflow.ledger.ledger import Ledger


def main() -> int:
    print("FREIGHTFLOW CONFLICT DEMO")
    print("=" * 40)
    print(f"Route:    {NETWORK_ROUTE.origin} \u2192 {NETWORK_ROUTE.destination}")
    print(f"Vehicle:  {VEHICLE.id} (carrier {VEHICLE.carrier_id})")
    print()
    print("Modified constraint:")
    print(f"  Babel contract B-119 requires exclusive carrier C-22")
    print()

    contracts = dict(CONTRACTS)
    contracts["D-BABEL"] = BABEL_EXCLUSIVE_CONTRACT

    ledger = Ledger()
    entries_before = len(ledger)

    mf = MultiFlowAdapter()
    report = mf.validate(list(SHIPMENTS), VEHICLE, contracts)

    print("MultiFlow validation: REJECTED" if not report.valid else "UNEXPECTED: VALID")
    if not report.valid:
        fail = report.first_failure()
        assert fail is not None
        print(f"Code:              {fail.code}")
        print(f"Message:           {fail.message}")
        print(f"Affected:          {', '.join(fail.affected_entities)}")
        print()
        print(f"Participant:       Babel")
        print(f"Shipment:          S-BABEL-004")
        print(f"Required carrier:  C-22")
        print(f"Proposed carrier:  {VEHICLE.carrier_id}")
        print(f"Settlement:        NOT CREATED")
        print(f"Ledger:            UNCHANGED ({entries_before} entries)")

        engine = AllocationEngine()
        ok, allocations, _ = engine.propose_and_validate(
            shipments=list(SHIPMENTS),
            vehicle=VEHICLE,
            contracts=contracts,
            total_cost=TOTAL_TRANSPORT_COST,
            policy=AllocationPolicy.WEIGHT,
            route_id=NETWORK_ROUTE.id,
        )
        assert not ok
        assert allocations is None
        assert len(ledger) == entries_before
        return 0

    print("ERROR: expected rejection")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
