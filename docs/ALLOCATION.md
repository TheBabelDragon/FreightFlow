# Allocation

## Central object

`Allocation` binds a shipment to a vehicle/route with exact weight, volume, and cost share (Decimal).

## Policies

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
