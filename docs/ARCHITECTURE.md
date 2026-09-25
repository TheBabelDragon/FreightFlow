# Architecture

## Core Rule

```
FreightFlow
     │
     ▼
MultiFlow
```

FreightFlow never forks MultiFlow’s solver core. It supplies the domain model and translates it into a MultiFlow problem. MultiFlow validates; FreightFlow interprets commercially.

## Domain Model (v0.1)

### Distributor
- id, name, contracts

### Shipment
- id, distributor_id, origin, destination
- weight, volume
- earliest_pickup, latest_delivery
- required_service, shareable

### Vehicle
- id, carrier_id
- max_weight, max_volume
- available_from, available_until, origin

### Contract
- id, distributor_id, carrier_id
- origin/destination constraints
- service_requirements, rate_model
- capacity_commitment, penalties

### Allocation (central object)
- shipment_id, vehicle_id, route_id
- allocated_weight, allocated_volume
- cost_share, contract_basis

## Deterministic Cost Allocation

```
total_transport_cost
        ↓
allocation basis
        ↓
participant shares
        ↓
exact monetary amounts
```

Supported bases:
- WEIGHT_PROPORTIONAL
- VOLUME_PROPORTIONAL
- WEIGHTED_COMPOSITE

Policy is recorded on the settlement record.

## Ledger

Append-only domain ledger (not blockchain).

Each entry answers: *Why does participant X owe $Y?*

Explanatory chain includes contract, shipment, vehicle, allocation policy, validated allocation id, and transport cost.

## MultiFlow Integration

FreightFlow → MultiFlow problem translation.
MultiFlow → candidate generation → independent validation → admissible allocation.
FreightFlow → commercial interpretation of validated allocation.

## Implementation Order

01. Repository scaffold  
02. Domain objects  
03. Deterministic money types  
04. Contract model  
05. Shipment model  
06. Vehicle model  
07. Allocation model  
08. Cost-allocation engine  
09. Ledger  
10. MultiFlow adapter  
11. Capacity validator  
12. Contract validator  
13. Time-window validator  
14. Shared-load engine  
15. End-to-end 3-distributor demo  
16. Rejection / explanation demo  
17. Event stream  
18. Deterministic replay  
19. ArcGIS adapter  
20. ArcGIS visualization  
21. Alternative candidate generation  
22. Financial reconciliation  
23. API / UI  
24. Transformer proposal adapter  

**Do not start with UI or Esri.** Solidify the 3-shipment → 1-truck → validate → settle loop first.
