# Recovery (PLANNED / FUTURE)

FreightFlow’s implemented financial path is deterministic and append-only:

```
physical / operational state
        → allocation
        → deterministic cost split
        → settlement
        → append-only ledger / audit
```

**Recovery is a documented extension point, not implemented in v0.2.**

## What recovery may cover (future)

| Concern | Intent |
|---------|--------|
| Disputed allocations | Challenge a posted settlement without rewriting it |
| Failed or partial payments | Record payment shortfalls relative to a settlement |
| Unreconciled carrier charges | Capture carrier-side amounts that diverge from settled shares |
| Settlement exceptions | Structured exception records linked to an original settlement |
| Recovery actions | Documented corrective events and their financial impact |

## Rules (binding design constraints)

1. **Never mutate the original settlement.** Posted settlements and their ledger entries remain immutable history.
2. **Recovery is new auditable events.** Adjustments, disputes, and recovery actions append new records that reference the original settlement/transaction ids.
3. **Preserve allocation, settlement, and ledger history.** Auditors must reconstruct the original operational outcome and every later exception event in order.
4. **Distinguish exception from payment rails.** Recovery events describe *what changed relative to a settlement*; they do not process bank transfers, collections, or carrier payouts.

## Conceptual chain (with recovery)

```
physical / operational state
        → allocation
        → deterministic cost split
        → settlement
        → append-only ledger / audit
        → recovery events when exceptions occur   ← PLANNED
```

## Status

| Capability | Status |
|------------|--------|
| Shared-load allocation | **IMPLEMENTED** |
| MultiFlow validation boundary | **IMPLEMENTED** |
| Deterministic cost split (`Decimal`) | **IMPLEMENTED** |
| Settlement + balanced ledger | **IMPLEMENTED** |
| Rejection without settlement | **IMPLEMENTED** |
| Recovery / dispute / payment events | **PLANNED / FUTURE** |
| Payment processing, collections, banking | **Out of scope** (not planned in this layer) |

v0.2 demos and tests do not exercise recovery APIs. Any future recovery module must obey the immutability rules above.
