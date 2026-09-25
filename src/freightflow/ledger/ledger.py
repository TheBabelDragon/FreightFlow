"""Append-only domain ledger."""

from __future__ import annotations

from freightflow.ledger.entries import LedgerEntry


class Ledger:
    """In-memory append-only ledger for v0.1."""

    def __init__(self) -> None:
        self._entries: list[LedgerEntry] = []

    def append(self, entry: LedgerEntry) -> None:
        self._entries.append(entry)

    def entries(self) -> list[LedgerEntry]:
        return list(self._entries)

    def for_participant(self, participant: str) -> list[LedgerEntry]:
        return [e for e in self._entries if e.participant == participant]

    def for_allocation(self, allocation_id: str) -> list[LedgerEntry]:
        return [e for e in self._entries if e.allocation_id == allocation_id]

    def balance(self, participant: str, account: str = "freight_payable") -> float:
        from decimal import Decimal

        total = Decimal("0")
        for e in self._entries:
            if e.participant == participant and e.account == account:
                total += e.debit - e.credit
        return float(total)
