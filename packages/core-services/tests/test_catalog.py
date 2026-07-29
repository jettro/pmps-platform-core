"""Tests for CatalogQuery.

Verifies case-insensitive substring search across name and SKU fields,
and currency-based filtering. Each test class uses its own pre-populated
fixture so test intent stays clear without repeated setup.
"""

from decimal import Decimal

import pytest

from framework_infra import InMemoryRepository

from core_domain.money import Money
from core_services.catalog import CatalogQuery
from core_services.product_service import ProductService


@pytest.fixture()
def catalog() -> CatalogQuery:
    """A CatalogQuery pre-loaded with three products across two currencies."""
    service = ProductService(InMemoryRepository())
    service.add("Blue Widget", "WGT-BLUE", Money(Decimal("9.99"), "EUR"))
    service.add("Red Gadget", "GDG-RED", Money(Decimal("19.99"), "USD"))
    service.add("Green Gizmo", "GZM-GREEN", Money(Decimal("5.50"), "EUR"))
    return CatalogQuery(service)


@pytest.fixture()
def empty_catalog() -> CatalogQuery:
    return CatalogQuery(ProductService(InMemoryRepository()))


class TestCatalogSearch:
    def test_search_by_name_substring(self, catalog: CatalogQuery) -> None:
        results = catalog.search("Widget")
        assert len(results) == 1
        assert results[0].name == "Blue Widget"

    def test_search_by_sku_substring(self, catalog: CatalogQuery) -> None:
        results = catalog.search("GDG")
        assert len(results) == 1
        assert results[0].sku == "GDG-RED"

    def test_search_case_insensitive_name(self, catalog: CatalogQuery) -> None:
        results_lower = catalog.search("widget")
        results_upper = catalog.search("WIDGET")
        assert len(results_lower) == len(results_upper) == 1

    def test_search_case_insensitive_sku(self, catalog: CatalogQuery) -> None:
        results = catalog.search("gzm-green")
        assert len(results) == 1
        assert results[0].name == "Green Gizmo"

    def test_search_matches_multiple_products(self, catalog: CatalogQuery) -> None:
        """'g' appears in Red Gadget, Green Gizmo, and SKUs — at least 2 name hits."""
        results = catalog.search("g")
        # Red Gadget, Green Gizmo + SKU hits — at minimum 2 distinct products
        assert len(results) >= 2

    def test_search_no_match_returns_empty(self, catalog: CatalogQuery) -> None:
        results = catalog.search("nonexistent-xyz")
        assert results == []

    def test_search_empty_query_returns_all(self, catalog: CatalogQuery) -> None:
        """An empty query string is a substring of every string."""
        results = catalog.search("")
        assert len(results) == 3

    def test_search_empty_catalog(self, empty_catalog: CatalogQuery) -> None:
        assert empty_catalog.search("anything") == []


class TestCatalogByCurrency:
    def test_by_currency_eur(self, catalog: CatalogQuery) -> None:
        results = catalog.by_currency("EUR")
        assert len(results) == 2
        assert all(p.price.currency == "EUR" for p in results)

    def test_by_currency_usd(self, catalog: CatalogQuery) -> None:
        results = catalog.by_currency("USD")
        assert len(results) == 1
        assert results[0].name == "Red Gadget"

    def test_by_currency_unknown_returns_empty(self, catalog: CatalogQuery) -> None:
        results = catalog.by_currency("JPY")
        assert results == []

    def test_by_currency_empty_catalog(self, empty_catalog: CatalogQuery) -> None:
        assert empty_catalog.by_currency("EUR") == []

    def test_by_currency_is_case_sensitive(self, catalog: CatalogQuery) -> None:
        """Currency codes are uppercase by convention; lowercase should not match."""
        results = catalog.by_currency("eur")
        assert results == []
