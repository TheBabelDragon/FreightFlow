# ArcGIS Adapter

## Boundary

```
ArcGIS service response  OR  fixture dict
        ↓
ArcGISAdapter.from_network_result(data, source=...)
        ↓
NetworkRoute
        ↓
FreightFlow
```

## v0.2 status

- Checked-in deterministic fixture: Dallas → Phoenix, 887 mi, 13.5 h
- `NetworkRoute.source == "fixture"` for demo data
- **No live ArcGIS API calls**
- **No API keys required for tests**
- Adapter is ready to accept normalized ArcGIS responses without domain changes

## Where ArcGIS enters the system

Only through `ArcGISAdapter.from_network_result`. Core domain models never import ArcGIS SDKs.
