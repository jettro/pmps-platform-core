"""Tests for the Money value object.

Covers arithmetic operators, same-currency enforcement, and string formatting.
"""

from decimal import Decimal

import pytest

from core_domain.money import Money


class TestMoneyAddition:
    def test_add_same_currency(self) -> None:
        a = Money(Decimal("10.00"), "EUR")
        b = Money(Decimal("5.50"), "EUR")
        result = a + b
        assert result == Money(Decimal("15.50"), "EUR")

    def test_add_preserves_currency(self) -> None:
        a = Money(Decimal("1.00"), "USD")
        b = Money(Decimal("2.00"), "USD")
        assert (a + b).currency == "USD"

    def test_add_different_currencies_raises(self) -> None:
        a = Money(Decimal("10.00"), "EUR")
        b = Money(Decimal("5.00"), "USD")
        with pytest.raises(AssertionError, match="EUR"):
            _ = a + b


class TestMoneySubtraction:
    def test_sub_same_currency(self) -> None:
        a = Money(Decimal("10.00"), "EUR")
        b = Money(Decimal("3.00"), "EUR")
        assert a - b == Money(Decimal("7.00"), "EUR")

    def test_sub_different_currencies_raises(self) -> None:
        a = Money(Decimal("10.00"), "EUR")
        b = Money(Decimal("3.00"), "GBP")
        with pytest.raises(AssertionError):
            _ = a - b


class TestMoneyMultiplication:
    def test_mul_integer_factor(self) -> None:
        price = Money(Decimal("9.99"), "EUR")
        assert price * Decimal("3") == Money(Decimal("29.97"), "EUR")

    def test_mul_fractional_factor(self) -> None:
        price = Money(Decimal("100.00"), "EUR")
        assert price * Decimal("0.5") == Money(Decimal("50.00"), "EUR")

    def test_mul_preserves_currency(self) -> None:
        price = Money(Decimal("10.00"), "GBP")
        assert (price * Decimal("2")).currency == "GBP"


class TestMoneyStringFormat:
    def test_str_two_decimal_places(self) -> None:
        m = Money(Decimal("10.5"), "EUR")
        assert str(m) == "EUR 10.50"

    def test_str_whole_number(self) -> None:
        m = Money(Decimal("100"), "USD")
        assert str(m) == "USD 100.00"

    def test_str_currency_prefix(self) -> None:
        m = Money(Decimal("1.23"), "GBP")
        assert str(m).startswith("GBP ")


class TestMoneyEquality:
    def test_equal_values(self) -> None:
        assert Money(Decimal("10.00"), "EUR") == Money(Decimal("10.00"), "EUR")

    def test_different_amounts_not_equal(self) -> None:
        assert Money(Decimal("10.00"), "EUR") != Money(Decimal("10.01"), "EUR")

    def test_different_currencies_not_equal(self) -> None:
        assert Money(Decimal("10.00"), "EUR") != Money(Decimal("10.00"), "USD")

    def test_frozen_cannot_mutate(self) -> None:
        m = Money(Decimal("10.00"), "EUR")
        with pytest.raises((AttributeError, TypeError)):
            m.amount = Decimal("99.00")  # type: ignore[misc]
