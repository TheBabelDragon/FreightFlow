# FreightFlow

FreightFlow is a cross-distributor freight coordination and settlement layer built on MultiFlow, designed to connect physical transportation networks with contractual allocation and auditable financial settlement.

```
              ARC GIS
                 │
        network + geography
                 │
                 ▼
          ┌──────────────┐
          │ FreightFlow  │
          │              │
          │ Contracts    │
          │ Shipments    │
          │ Vehicles     │
          │ Economics    │
          └──────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │   MultiFlow  │
          │              │
          │ Propose      │
          │ Validate     │
          │ Explain      │
          └──────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │   Settlement │
          │              │
          │ Allocation   │
          │ Ledger       │
          │ Audit trail  │
          └──────────────┘
```

## Core Principle

**FreightFlow supplies the domain model and translates it into a MultiFlow problem.**  
**Never fork MultiFlow’s core logic.**

```
FreightFlow
     │
     ▼
MultiFlow
```

MultiFlow validates the allocation. FreightFlow interprets the validated allocation commercially.

## Objective (v0.1)

Given multiple distributors, their freight obligations, available vehicles, a shared transportation network, and contractual constraints, produce an **admissible shared-load allocation** and an **auditable financial settlement**.

## Killer Demo Loop

```
3 shipments
      ↓
1 shared truck
      ↓
MultiFlow validates
      ↓
cost allocation
      ↓
ledger
      ↓
auditable settlement
```

### Example Output

```
┌─────────────────────────────────────┐
│ SHARED FREIGHT ALLOCATION           │
├─────────────────────────────────────┤
│ Route       Dallas → Phoenix        │
│ Vehicle     Truck-17                │
│ Capacity    20 pallets              │
│ Utilization 100%                    │
│                                     │
│ ACME             8 pallets   $480   │
│ Babel            5 pallets   $300   │
│ Desert           7 pallets   $420   │
│                                     │
│ Total                       $1,200   │
└─────────────────────────────────────┘

VALIDATED → SETTLED
```

## Repository Layout

```
FreightFlow/
├── src/freightflow/
│   ├── domain/          # Distributor, Shipment, Vehicle, Contract, Allocation, Settlement
│   ├── constraints/     # Capacity, contract, delivery, allocation validators
│   ├── allocation/      # Load matcher, cost allocator, allocation engine
│   ├── ledger/          # Append-only domain ledger + audit trail
│   ├── adapters/        # MultiFlow + ArcGIS adapters
│   └── api/
├── examples/            # shared_freight_demo.py
├── tests/
└── docs/
```

## Deterministic Money

Financial amounts are never invented by optimizers or LLMs.

```
total_transport_cost
        ↓
allocation basis (WEIGHT | VOLUME | WEIGHTED_COMPOSITE)
        ↓
participant shares
        ↓
exact monetary amounts
```

The allocation policy itself is recorded in the settlement and ledger.

## Status

Scaffolded for v0.1. Implementation order is documented in `docs/ARCHITECTURE.md`.

## License

See [LICENSE](LICENSE).
