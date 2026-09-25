# Allocation

## Central Object

`Allocation` binds a shipment to a vehicle/route with exact weight, volume, and cost share.

## Deterministic Policies

| Policy | Formula |
|--------|---------|
| WEIGHT_PROPORTIONAL | `shipment_weight / total_allocated_weight` |
| VOLUME_PROPORTIONAL | `shipment_volume / total_allocated_volume` |
| WEIGHTED_COMPOSITE | `(w×wf) + (v×vf) + (d×df)` normalized |

Policy is recorded on every settlement and ledger entry.

## Flow

```
shipments + vehicle + contracts
        ↓
LoadMatcher (candidate groups)
        ↓
Capacity / Contract / Shareability validators
        ↓
CostAllocator (deterministic shares)
        ↓
list[Allocation]
```

MultiFlow validates admissibility; FreightFlow never lets an optimizer invent money.
