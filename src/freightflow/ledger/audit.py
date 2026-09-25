"""Audit / explanation helpers."""

from __future__ import annotations

from freightflow.ledger.ledger import Ledger


class AuditTrail:
    """Answer: Why does participant X owe $Y?"""

    def __init__(self, ledger: Ledger) -> None:
        self.ledger = ledger

    def explain(self, participant: str) -> list[str]:
        lines: list[str] = []
        for e in self.ledger.for_participant(participant):
            if e.debit > 0:
                lines.append(
                    f"{e.entry_id}: {participant} owes {e.debit} {e.currency} "
                    f"({e.explanation})"
                )
        return lines
