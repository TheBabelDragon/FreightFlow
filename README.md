# FreightFlow

**Status: Working v0.2 demonstrator**

Cross-distributor freight **coordination and settlement** on MultiFlow.

FreightFlow addresses a concrete operational problem: multiple distributors share capacity on the same physical move, need an admissible allocation under contracts and capacity, and need a deterministic, auditable split of cost—without forking the underlying network or solver stack.

> Esri knows where freight can move.  
> FreightFlow coordinates who can share it.  
> MultiFlow determines whether the allocation is admissible.  
> The ledger records what each participant owes.

**Launch page (GitHub Pages):** [https://thebabeldragon.github.io/FreightFlow/](https://thebabeldragon.github.io/FreightFlow/)

Source: [`docs/site/index.html`](docs/site/index.html) · Workflow: [`.github/workflows/pages.yml`](.github/workflows/pages.yml)

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

Optional editable install (if `hatchling` is available): `python -m pip install -e ".[dev]"` (then `PYTHONPATH` is not required).

---

## What is implemented

| Capability | Status |
|------------|--------|
| Shared-load coordination (shipments + vehicle + route) | **IMPLEMENTED** |
| Domain constraints (capacity, contract, windows, shareability) | **IMPLEMENTED** |
| MultiFlow validation boundary (admissibility / rejection codes) | **IMPLEMENTED** |
| Deterministic cost allocation (`Decimal`, recorded policy) | **IMPLEMENTED** |
| Settlement + balanced append-only ledger + explanations | **IMPLEMENTED** |
| ArcGIS network fixture adapter | **IMPLEMENTED** |
| Live ArcGIS routing, carrier APIs, TMS, payments | **Not implemented** |
| Recovery / dispute / exception events | **PLANNED** — see [docs/RECOVERY.md](docs/RECOVERY.md) |

---

## Operational and financial chain

```
physical / operational state (network, capacity, contracts)
        → allocation (shared load)
        → deterministic cost split
        → settlement
        → append-only ledger / audit
        → recovery events when exceptions occur   ← PLANNED
```

**Rule:** rejected allocations never create settlement or ledger entries.  
**Rule (future recovery):** never mutate the original settlement; recovery is new auditable events only.

---

## Demonstrator results

### Shared freight (happy path)

Three **participants** share one **load** Dallas → Phoenix on **Truck-17** (20-pallet capacity):

| Participant | Pallets | Share | Cost |
|-------------|---------|-------|------|
| ACME        | 8       | 40%   | **$480** |
| Babel       | 5       | 25%   | **$300** |
| Desert      | 7       | 35%   | **$420** |
| **Total**   | **20**  | **100%** | **$1,200** |

Policy: **WEIGHT** · Validation: **VALID** · Ledger: **BALANCED**

### Contract conflict (rejection)

Babel requires exclusive carrier **C-22**; proposed carrier is **TruckCo-17**.

Result: **REJECTED** · code `CONTRACT-CARRIER-EXCLUSIVITY` · **no settlement, no ledger entries**

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

FreightFlow is a **vertical domain layer**. It does **not** fork MultiFlow.  
ArcGIS supplies network context; MultiFlow owns admissibility; FreightFlow owns commercial interpretation and settlement.

Why this can extend toward real-world freight/industrial coordination: the same boundaries separate geography, validation, economics, and (later) exception recovery without rewriting operational history.

---

## Documentation

| Doc | Content |
|-----|---------|
| [ARCHITECTURE](docs/ARCHITECTURE.md) | Stack, domain terms, status |
| [ALLOCATION](docs/ALLOCATION.md) | Policies and allocation flow |
| [LEDGER](docs/LEDGER.md) | Settlement, balance, explanations |
| [ARCGIS](docs/ARCGIS.md) | Network adapter / fixture boundary |
| [RECOVERY](docs/RECOVERY.md) | **PLANNED** recovery / exception model |

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
