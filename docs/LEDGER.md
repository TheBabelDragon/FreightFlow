# Ledger

Append-only domain ledger (not blockchain).

## Entry Shape

```
LedgerEntry
├── entry_id
├── transaction_id
├── timestamp
├── participant
├── account
├── debit / credit
├── currency
├── allocation_id
└── explanation
```

## Example

$1,200 shared truck:

| Participant | Debit | Credit | Explanation |
|-------------|-------|--------|-------------|
| CARRIER | — | 1200 | Transport revenue |
| ACME | 480 | — | Weight share 8/20 |
| Babel | 300 | — | Weight share 5/20 |
| Desert | 420 | — | Weight share 7/20 |

## Audit Question

> Why does Distributor B owe $300?

```
Contract B-119
+ Shipment B-004
+ Vehicle V-17
+ Allocation policy: WEIGHT_PROPORTIONAL
+ Validated allocation: ALLOC-918
+ Transport cost: $1,200
+ B share: 25%
= $300
```

The explanatory chain is a core product feature.
