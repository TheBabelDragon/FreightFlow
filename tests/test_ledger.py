"""Ledger unit tests."""

from decimal import Decimal

from freightflow.ledger.entries import LedgerEntry
from freightflow.ledger.ledger import Ledger


def test_append_and_query():
    ledger = Ledger()
    e = LedgerEntry(
        transaction_id="TX1",
        participant="A",
        account="freight_payable",
        debit=Decimal("100"),
        explanation="test",
    )
    ledger.append(e)
    assert len(ledger.entries()) == 1
    assert ledger.for_participant("A")[0].debit == Decimal("100")
    assert ledger.balance("A") == Decimal("100")
    assert ledger.is_balanced() is False

    ledger.append(
        LedgerEntry(
            transaction_id="TX1",
            participant="CARRIER",
            account="freight_receivable",
            credit=Decimal("100"),
        )
    )
    assert ledger.is_balanced("TX1") is True
