"""Append-only domain ledger."""

from __future__ import annotations

from decimal import Decimal

from freightflow.ledger.entries import LedgerEntry


class Ledger:
    """In-memory append-only ledger. No hidden global state \u2014 pass explicitly."""

    def __init__(self) -> None:
        self._entries: list[LedgerEntry] = []

    def append(self, entry: LedgerEntry) -> None:
        self._entries.append(entry)

    def entries(self) -> list[LedgerEntry]:
        return list(self._entries)

    def entries_for_transaction(self, transaction_id: str) -> list[LedgerEntry]:
        return [e for e in self._entries if e.transaction_id == transaction_id]

    def for_participant(self, participant: str) -> list[LedgerEntry]:
        return [e for e in self._entries if e.participant == participant]

    def for_allocation(self, allocation_id: str) -> list[LedgerEntry]:
        return [e for e in self._entries if e.allocation_id == allocation_id]

    def balance(self, participant: str, account: str = "freight_payable") -> Decimal:
        total = Decimal("0")
        for e in self._entries:
            if e.participant == participant and e.account == account:
                total += e.debit - e.credit
        return total

    def is_balanced(self, transaction_id: str | None = None) -> bool:
        """True when total debits == total credits (optionally for one txn)."""
        subset = (
            self.entries_for_transaction(transaction_id)
            if transaction_id
            else self._entries
        )
        debits = sum((e.debit for e in subset), Decimal("0"))
        credits = sum((e.credit for e in subset), Decimal("0"))
        return debits == credits

    def explain_entry(self, entry_id: str) -> str | None:
        for e in self._entries:
            if e.entry_id == entry_id:
                return (
                    f"{e.entry_id}: {e.participant} "
                    f"debit={e.debit} credit={e.credit} {e.currency} "
                    f"| {e.explanation}"
                )
        return None

    def __len__(self) -> int:
        return len(self._entries)
