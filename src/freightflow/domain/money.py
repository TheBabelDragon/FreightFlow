"""Deterministic money types. Never use float for financial amounts."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Self

from pydantic import BaseModel, Field, field_validator


class Money(BaseModel):
    """Exact monetary amount with currency. Immutable value object."""

    model_config = {"frozen": True}

    amount: Decimal = Field(..., description="Exact amount; never float")
    currency: str = Field(default="USD", min_length=3, max_length=3)

    @field_validator("amount", mode="before")
    @classmethod
    def _coerce_decimal(cls, v: object) -> Decimal:
        if isinstance(v, float):
            raise TypeError("Money amount must not be float; use Decimal or str")
        return Decimal(str(v))

    def quantize(self, places: str = "0.01") -> Self:
        return Money(
            amount=self.amount.quantize(Decimal(places), rounding=ROUND_HALF_UP),
            currency=self.currency,
        )

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: {self.currency} vs {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: {self.currency} vs {other.currency}")
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def __mul__(self, factor: Decimal | int) -> Money:
        return Money(amount=self.amount * Decimal(str(factor)), currency=self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount.quantize(Decimal('0.01'))}"

    def __repr__(self) -> str:
        return f"Money({self.amount!r}, {self.currency!r})"
