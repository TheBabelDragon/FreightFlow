# FreightFlow

**Status: Working v0.2 demonstrator**

Cross-distributor freight coordination and settlement on MultiFlow.

> Esri knows where freight can move.  
> FreightFlow coordinates how multiple distributors can share that movement and settle the resulting cost.  
> MultiFlow provides the admissibility/validation boundary.

**Launch page (GitHub Pages):** [https://thebabeldragon.github.io/FreightFlow/](https://thebabeldragon.github.io/FreightFlow/)

Source HTML: [`docs/site/index.html`](docs/site/index.html) · Deployed by [`.github/workflows/pages.yml`](.github/workflows/pages.yml)

---

## Quick start

**Prerequisites:** Python 3.11+, Git

```bash
git clone https://github.com/TheBabelDragon/FreightFlow.git
cd FreightFlow
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
# .venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install pydantic pytest
export PYTHONPATH=src          # Linux / macOS
# set PYTHONPATH=src           # Windows cmd
# $env:PYTHONPATH="src"        # Windows PowerShell

python examples/shared_freight_demo.py
python examples/conflict_demo.py
pytest -q
```

Optional editable install (if `hatchling` is available):

```bash
python -m pip install -e ".[dev]"
# then PYTHONPATH is not required
```

---

## What the demo shows

### Shared freight (happy path)

Three distributors share one truck Dallas → Phoenix:

| Participant | Pallets | Share | Cost |
|-------------|---------|-------|------|
| ACME        | 8       | 40%   | **$480** |
| Babel       | 5       | 25%   | **$300** |
| Desert      | 7       | 35%   | **$420** |
| **Total**   | **20**  | **100%** | **$1,200** |

Vehicle: **Truck-17** (20-pallet capacity) · Policy: **WEIGHT** · Ledger: **BALANCED**

### Contract conflict (rejection)

Babel requires exclusive carrier **C-22**. Proposed carrier is **TruckCo-17**.

Result: **REJECTED** with code `CONTRACT-CARRIER-EXCLUSIVITY` — **no settlement, no ledger entries**.

---

## Architecture

```
              ARC GIS
                 │
        network + geography  (fixture in v0.2)
                 │
                 ▼
          ┌──────────────┐
          │ FreightFlow  │  shipments · contracts · vehicles · economics
          └──────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │   MultiFlow  │  propose · validate · explain (admissibility)
          └──────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │  Settlement  │  allocation · ledger · audit trail
          └──────────────┘
```

| Layer | Responsibility |
|-------|----------------|
| **ArcGIS** | Physical network / geography / routing. v0.2 uses a **deterministic fixture** (`source=fixture`). No live ArcGIS API calls. |
| **FreightFlow** | Domain: shipments, contracts, vehicles, deterministic cost allocation, settlement. |
| **MultiFlow** | Admissibility boundary. FreightFlow does **not** fork MultiFlow. |
| **Ledger** | Append-only, balanced entries. Rejected allocations never post. |

**Not claimed in v0.2:** live ArcGIS routing, live carrier APIs, production TMS, blockchain, LLM optimization, payment rails.

---

## Deterministic money

All amounts use `Decimal` (no float). Policy is recorded on every settlement.

```
total $1,200  →  WEIGHT basis  →  $480 + $300 + $420  =  $1,200
```

---

## Key commands

```bash
python examples/shared_freight_demo.py   # $480 / $300 / $420, BALANCED
python examples/conflict_demo.py         # CONTRACT-CARRIER-EXCLUSIVITY, no settlement
pytest -q                                # full suite
```

---

## License

MIT — see [LICENSE](LICENSE).
