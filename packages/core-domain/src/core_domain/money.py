"""Monetary value object.

Money is a classic domain value object: it has no identity of its own, only
a value (amount + currency). Being frozen ensures it is safe to embed in other
frozen dataclasses (e.g. Product price) and that arithmetic always produces a
new instance rather than mutating state.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """An immutable monetary amount with an ISO-4217 currency code.

    All arithmetic operations enforce same-currency invariant at runtime.
    This is intentional: silent cross-currency math is a class of bug that
    has caused real financial losses; an AssertionError is far preferable.

    Args:
        amount: The numeric value (use Decimal to avoid float rounding).
        currency: Three-letter ISO currency code, e.g. "EUR", "USD".
    """

    amount: Decimal
    currency: str

    def __add__(self, other: Money) -> Money:
        """Add two monetary amounts.

        Raises:
            AssertionError: If the currencies differ.
        """
        assert self.currency == other.currency, (
            f"Cannot add {self.currency} and {other.currency}"
        )
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        """Subtract another monetary amount from this one.

        Raises:
            AssertionError: If the currencies differ.
        """
        assert self.currency == other.currency, (
            f"Cannot subtract {other.currency} from {self.currency}"
        )
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal) -> Money:
        """Scale the amount by a Decimal factor (e.g. for quantity pricing).

        Args:
            factor: A Decimal multiplier. Use Decimal("2") not 2.0 to preserve
                    exact arithmetic.
        """
        return Money(self.amount * factor, self.currency)

    def __str__(self) -> str:
        """Human-readable representation: '<CURRENCY> <amount:.2f>'.

        Example: Money(Decimal("10.5"), "EUR") -> "EUR 10.50"
        """
        return f"{self.currency} {self.amount:.2f}"
