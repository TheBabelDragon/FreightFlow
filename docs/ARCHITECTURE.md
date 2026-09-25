# Architecture

## Positioning

```
ArcGIS knows where freight can move.
FreightFlow coordinates who can share it.
MultiFlow determines whether the allocation is admissible.
The ledger records what each participant owes.
```

## Core rule

```
FreightFlow
     │
     ▼
MultiFlow
```

FreightFlow never forks MultiFlow’s solver core. It supplies the domain model and translates it into a MultiFlow problem. MultiFlow validates; FreightFlow interprets commercially.

## Operational flow (IMPLEMENTED)

```
network / geography (ArcGIS or fixture)
        → shipments + vehicles + contracts
        → candidate shared load
        → MultiFlow / domain validation
        → deterministic cost allocation
        → settlement
        → append-only ledger / audit
```

Rejected candidates produce machine-readable codes and **no** settlement.

## Domain (v0.2)

| Term | Meaning |
|------|---------|
| **Participant** | Distributor sharing a load (e.g. ACME, Babel, Desert) |
| **Shipment** | Freight obligation (origin, destination, weight/volume, windows, shareable) |
| **Load** | Shared set of shipments on one vehicle/route |
| **Vehicle** | Capacity and carrier identity |
| **Contract** | Carrier restrictions, exclusivity, allowed OD pairs |
| **Allocation** | Shipment↔vehicle binding with `cost_share` (Decimal) and policy |
| **Settlement** | Posted participant shares, policy, reconciliation, status |
| **Ledger** | Append-only audit of financial entries for a transaction |
| **Exception / recovery** | Future: new events linked to a settlement — never mutate the original |

## Constraint codes (stable)

| Code | Meaning |
|------|---------|
| CAPACITY-OVERFLOW | Weight or volume exceeds vehicle |
| DELIVERY-WINDOW | Pickup/delivery outside allowed window |
| CONTRACT-CARRIER-EXCLUSIVITY | Carrier not permitted by contract |
| SHIPMENT-NOT-SHAREABLE | Non-shareable freight co-loaded |
| ALLOCATION-INCOMPLETE | Required shipments missing from allocation |

## Money

All financial amounts use `Decimal`. Float is rejected at validation boundaries. Cost policies: WEIGHT, VOLUME, WEIGHTED_COMPOSITE. `sum(shares) == total_cost` is guaranteed; remainder assigned deterministically.

## ArcGIS boundary

`ArcGISAdapter.from_network_result` is the single entry point. Fixture data uses `source="fixture"`. Live ArcGIS is not required for tests or demos.

## Recovery boundary (PLANNED)

See [RECOVERY.md](RECOVERY.md). Recovery must append auditable events; it must never rewrite allocation, settlement, or ledger history.

## Status summary

| Area | Status |
|------|--------|
| Domain model, validators, allocation, settlement, ledger | **IMPLEMENTED** |
| Shared-load + conflict demos | **IMPLEMENTED** |
| ArcGIS fixture adapter | **IMPLEMENTED** |
| Live ArcGIS / carrier APIs / TMS / payments | **Not implemented** |
| Recovery / dispute events | **PLANNED / FUTURE** |
