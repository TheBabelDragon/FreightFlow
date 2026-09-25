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

## Domain (v0.2)

- **Distributor** — id, name, contracts
- **Shipment** — id, distributor, origin/destination, weight, volume, windows, shareable
- **Vehicle** — id, carrier, capacity, availability, origin
- **Contract** — carrier restrictions, exclusivity, origins/destinations
- **Allocation** — shipment↔vehicle binding with cost_share (Decimal), policy
- **Settlement** — participant_shares, policy, reconciliation, status
- **NetworkRoute** — ArcGIS/fixture boundary object
- **Money** — Decimal amount + currency (no float)
- **ValidationResult** — valid, code, message, affected_entities

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
