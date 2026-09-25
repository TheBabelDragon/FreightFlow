# Allocation

## Central object

`Allocation` binds a **shipment** to a vehicle/route with exact weight, volume, and cost share (`Decimal`).

A **load** is the set of shipments sharing one vehicle on one route.

## Policies (IMPLEMENTED)

| Policy | Basis |
|--------|-------|
| WEIGHT | shipment_weight / total_weight |
| VOLUME | shipment_volume / total_volume |
| WEIGHTED_COMPOSITE | (w×wf)+(v×vf)+(d×df) normalized |

Policy is recorded on every settlement and ledger entry.

## Flow

```
shipments + vehicle + contracts
        ↓
validators (structured ValidationResult)
        ↓
CostAllocator (deterministic shares)
        ↓
list[Allocation]  OR  rejection (no settlement)
```

Reference demonstrator: 8 + 5 + 7 pallets on a 20-pallet truck → 40% / 25% / 35% of $1,200 → $480 / $300 / $420.
