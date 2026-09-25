# ArcGIS Adapter

Keep ArcGIS **out of the core domain model**.

```
ArcGIS
  ↓ network information
FreightFlow route model

FreightFlow
  ↓ selected route/allocation
ArcGIS visualization
```

## Initial Scope

- origin / destination
- route
- distance
- travel time
- network constraints

Do not build a large Esri integration before the underlying freight transaction works.
