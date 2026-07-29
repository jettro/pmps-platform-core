"""Tests for ProductService.

Uses InMemoryRepository from framework_infra so tests remain fast and
isolated without touching a filesystem or network.  Each test gets a fresh
repository via the fixture, preventing state leakage between tests.
"""

from decimal import Decimal

import pytest

from framework_infra import InMemoryRepository

from core_domain.money import Money
from core_domain.product import Product
from core_services.product_service import ProductService


@pytest.fixture()
def repo() -> InMemoryRepository:
    return InMemoryRepository()


@pytest.fixture()
def service(repo: InMemoryRepository) -> ProductService:
    return ProductService(repo)


@pytest.fixture()
def eur_price() -> Money:
    return Money(Decimal("9.99"), "EUR")


class TestProductServiceAdd:
    def test_add_returns_success(self, service: ProductService, eur_price: Money) -> None:
        result = service.add("Widget", "WGT-001", eur_price)
        assert result.is_ok() is True

    def test_add_success_contains_product(self, service: ProductService, eur_price: Money) -> None:
        result = service.add("Widget", "WGT-001", eur_price)
        assert result.value.name == "Widget"
        assert result.value.sku == "WGT-001"
        assert result.value.price == eur_price

    def test_add_product_gets_id(self, service: ProductService, eur_price: Money) -> None:
        result = service.add("Widget", "WGT-001", eur_price)
        assert result.value.id is not None

    def test_add_with_description(self, service: ProductService, eur_price: Money) -> None:
        result = service.add("Widget", "WGT-001", eur_price, description="A fine widget")
        assert result.value.description == "A fine widget"

    def test_add_empty_name_returns_failure(self, service: ProductService, eur_price: Money) -> None:
        result = service.add("", "WGT-001", eur_price)
        assert result.is_ok() is False

    def test_add_whitespace_name_returns_failure(self, service: ProductService, eur_price: Money) -> None:
        result = service.add("   ", "WGT-001", eur_price)
        assert result.is_ok() is False

    def test_add_empty_sku_returns_failure(self, service: ProductService, eur_price: Money) -> None:
        result = service.add("Widget", "", eur_price)
        assert result.is_ok() is False

    def test_add_failure_contains_error_message(self, service: ProductService, eur_price: Money) -> None:
        result = service.add("", "WGT-001", eur_price)
        assert isinstance(result.error, str)
        assert len(result.error) > 0


class TestProductServiceGet:
    def test_get_existing_product(self, service: ProductService, eur_price: Money) -> None:
        result = service.add("Widget", "WGT-001", eur_price)
        product_id = result.value.id
        found = service.get(product_id)
        assert found is not None
        assert found.id == product_id

    def test_get_missing_product_returns_none(self, service: ProductService) -> None:
        assert service.get("does-not-exist") is None

    def test_get_returns_correct_fields(self, service: ProductService, eur_price: Money) -> None:
        service.add("Widget", "WGT-001", eur_price)
        result = service.add("Gadget", "GDG-001", Money(Decimal("19.99"), "EUR"))
        found = service.get(result.value.id)
        assert found.name == "Gadget"
        assert found.sku == "GDG-001"


class TestProductServiceList:
    def test_list_empty_catalog(self, service: ProductService) -> None:
        assert service.list() == []

    def test_list_after_single_add(self, service: ProductService, eur_price: Money) -> None:
        service.add("Widget", "WGT-001", eur_price)
        assert len(service.list()) == 1

    def test_list_after_multiple_adds(self, service: ProductService, eur_price: Money) -> None:
        service.add("Widget", "WGT-001", eur_price)
        service.add("Gadget", "GDG-001", eur_price)
        service.add("Gizmo", "GZM-001", eur_price)
        assert len(service.list()) == 3

    def test_list_returns_product_instances(self, service: ProductService, eur_price: Money) -> None:
        service.add("Widget", "WGT-001", eur_price)
        products = service.list()
        assert all(isinstance(p, Product) for p in products)


class TestProductServiceRemove:
    def test_remove_existing_returns_true(self, service: ProductService, eur_price: Money) -> None:
        result = service.add("Widget", "WGT-001", eur_price)
        assert service.remove(result.value.id) is True

    def test_remove_non_existing_returns_false(self, service: ProductService) -> None:
        assert service.remove("ghost-id") is False

    def test_remove_decreases_list_count(self, service: ProductService, eur_price: Money) -> None:
        r1 = service.add("Widget", "WGT-001", eur_price)
        service.add("Gadget", "GDG-001", eur_price)
        service.remove(r1.value.id)
        assert len(service.list()) == 1

    def test_get_after_remove_returns_none(self, service: ProductService, eur_price: Money) -> None:
        result = service.add("Widget", "WGT-001", eur_price)
        pid = result.value.id
        service.remove(pid)
        assert service.get(pid) is None
