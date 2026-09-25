# Ledger

Append-only domain ledger (not blockchain).

## API

- `ledger.is_balanced(transaction_id?)`
- `ledger.entries_for_transaction(txn_id)`
- `ledger.explain_entry(entry_id)`
- `settlement.reconciliation()` → proves sum(shares) == total

## Rule

Rejected allocations **never** post ledger entries.

## Explanation

`SettlementExplanation` answers “Why does X owe $Y?” from structured facts: contract, shipment, vehicle, route, policy, quantities, transport cost, allocation id, settlement id.
