# FreightFlow

**v0.2 — Esri-ready demonstrator**

FreightFlow is a cross-distributor freight coordination and settlement layer built on MultiFlow. It connects physical transportation networks with contractual allocation and auditable financial settlement.

```
ArcGIS knows where freight can move.
FreightFlow coordinates who can share it.
MultiFlow determines whether the allocation is admissible.
The ledger records what each participant owes.
```

```
              ARC GIS
                 │
        network + geography
                 │
                 ▼
          ┌──────────────┐
          │ FreightFlow  │
          │ Contracts    │
          │ Shipments    │
          │ Vehicles     │
          │ Economics    │
          └──────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │   MultiFlow  │
          │ Propose      │
          │ Validate     │
          │ Explain      │
          └──────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │  Settlement  │
          │ Allocation   │
          │ Ledger       │
          │ Audit trail  │
          └──────────────┘
```

## Core principle

**FreightFlow supplies the domain model and translates it into a MultiFlow problem.**  
**Never fork MultiFlow’s core logic.**

MultiFlow validates the allocation. FreightFlow interprets the validated allocation commercially.

## Killer loop

```
3 shipments
      ↓
1 shared truck
      ↓
MultiFlow validates
      ↓
deterministic cost allocation
      ↓
ledger
      ↓
auditable settlement
```

## Reference scenario

| Participant | Pallets | Share | Cost |
|-------------|---------|-------|------|
| ACME        | 8       | 40%   | $480 |
| Babel       | 5       | 25%   | $300 |
| Desert      | 7       | 35%   | $420 |
| **Total**   | **20**  | **100%** | **$1,200** |

Route: Dallas → Phoenix · Vehicle: Truck-17 · Capacity: 20 pallets · Policy: WEIGHT

## Successful output

```
FREIGHTFLOW SHARED LOAD
========================================
Route:       Dallas → Phoenix
Vehicle:     Truck-17
Capacity:    20 pallets
Utilization: 100%

ACME          8 pallets     $480.00
Babel         5 pallets     $300.00
Desert        7 pallets     $420.00
Transport cost:             $1200.00

MultiFlow validation:  VALID
Settlement:            POSTED
Ledger:                BALANCED
```

## Conflict / rejection output

```
FREIGHTFLOW CONFLICT DEMO
========================================
MultiFlow validation: REJECTED
Code:              CONTRACT-CARRIER-EXCLUSIVITY
Participant:       Babel
Shipment:          S-BABEL-004
Required carrier:  C-22
Proposed carrier:  TruckCo-17
Settlement:        NOT CREATED
Ledger:            UNCHANGED
```

Rejected allocations **never** create financial entries.

## Deterministic money

Financial amounts are never invented by optimizers or LLMs.

```
total_transport_cost
        ↓
allocation basis (WEIGHT | VOLUME | WEIGHTED_COMPOSITE)
        ↓
participant shares
        ↓
exact monetary amounts  (sum == total; remainder assigned deterministically)
```

The allocation policy is recorded on every settlement and ledger entry. **No floats.**

## Ledger explanation

> Why does Babel owe $300?

```
Participant: Babel Supply
Amount: USD 300.00
Shipment: S-BABEL-004
Vehicle: Truck-17
Route: Dallas → Phoenix
Allocation: 500 / 2000 = 25%
Policy: WEIGHT
Transport cost: USD 1200.00
Settlement: SET-...
```

Built from structured facts — not LLM prose.

## ArcGIS integration boundary

```
ArcGIS service (or fixture)
        ↓
ArcGISAdapter.from_network_result(...)
        ↓
NetworkRoute   (source='fixture' | 'arcgis')
        ↓
FreightFlow allocation
```

v0.2 ships with a **checked-in deterministic network fixture**. Live ArcGIS routing is not performed and is not claimed. The adapter is the documented entry point for real service responses.

## MultiFlow relationship

```
FreightFlow domain objects
        ↓
MultiFlowAdapter.to_problem / validate
        ↓
admissibility (MultiFlow owns this)
        ↓
FreightFlow commercial interpretation (cost, ledger, settlement)
```

No MultiFlow source is copied or forked.

## Quick start

```bash
git clone https://github.com/TheBabelDragon/FreightFlow.git
cd FreightFlow
pip install pydantic pytest
export PYTHONPATH=src

python examples/shared_freight_demo.py
python examples/conflict_demo.py
pytest -q
```

## License

MIT — see [LICENSE](LICENSE).
