# Ledger

Append-only domain ledger (not blockchain).

## IMPLEMENTED

### API

- `ledger.is_balanced(transaction_id?)`
- `ledger.entries_for_transaction(txn_id)`
- `ledger.explain_entry(entry_id)`
- `settlement.reconciliation()` → proves `sum(shares) == total`

### Rule

Rejected allocations **never** post ledger entries.

### Explanation

`SettlementExplanation` answers “Why does participant X owe amount Y?” from structured facts: contract, shipment, vehicle, route, policy, quantities, transport cost, allocation id, settlement id.

### Conceptual chain

```
physical / operational state
        → allocation
        → deterministic cost split
        → settlement
        → append-only ledger / audit
```

Money uses `Decimal`. Policy (WEIGHT | VOLUME | WEIGHTED_COMPOSITE) is recorded on every settlement.

## PLANNED / FUTURE

Recovery and exception handling must **not** rewrite posted settlements or ledger entries. See [RECOVERY.md](RECOVERY.md): recovery is represented as new auditable events that reference original settlement and transaction ids.
