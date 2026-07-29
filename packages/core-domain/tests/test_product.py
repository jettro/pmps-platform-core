"""Tests for the Product entity.

Covers creation, auto-generated id, serialization round-trip, and that
Product identity is based solely on id (Entity semantics).
"""

from decimal import Decimal

import pytest

from core_domain.money import Money
from core_domain.product import Product


@pytest.fixture()
def sample_price() -> Money:
    return Money(Decimal("9.99"), "EUR")


@pytest.fixture()
def sample_product(sample_price: Money) -> Product:
    return Product(
        name="Blue Widget",
        sku="WGT-BLUE-001",
        price=sample_price,
        description="A premium blue widget",
    )


class TestProductCreation:
    def test_fields_are_stored(self, sample_product: Product, sample_price: Money) -> None:
        assert sample_product.name == "Blue Widget"
        assert sample_product.sku == "WGT-BLUE-001"
        assert sample_product.price == sample_price
        assert sample_product.description == "A premium blue widget"

    def test_id_is_auto_generated(self, sample_product: Product) -> None:
        assert sample_product.id is not None
        assert len(sample_product.id) > 0

    def test_two_products_have_different_ids(self, sample_price: Money) -> None:
        p1 = Product(name="A", sku="A-001", price=sample_price)
        p2 = Product(name="A", sku="A-001", price=sample_price)
        assert p1.id != p2.id

    def test_default_description_is_empty(self, sample_price: Money) -> None:
        p = Product(name="Minimal", sku="MIN-001", price=sample_price)
        assert p.description == ""

    def test_explicit_id_is_respected(self, sample_price: Money) -> None:
        p = Product(id="custom-id", name="Thing", sku="THG-001", price=sample_price)
        assert p.id == "custom-id"


class TestProductSerialization:
    def test_to_dict_contains_all_fields(self, sample_product: Product) -> None:
        d = sample_product.to_dict()
        assert d["id"] == sample_product.id
        assert d["name"] == "Blue Widget"
        assert d["sku"] == "WGT-BLUE-001"
        assert d["description"] == "A premium blue widget"

    def test_to_dict_money_is_nested(self, sample_product: Product) -> None:
        d = sample_product.to_dict()
        assert isinstance(d["price"], dict)
        assert d["price"]["amount"] == "9.99"
        assert d["price"]["currency"] == "EUR"

    def test_from_dict_round_trip(self, sample_product: Product) -> None:
        restored = Product.from_dict(sample_product.to_dict())
        assert restored.id == sample_product.id
        assert restored.name == sample_product.name
        assert restored.sku == sample_product.sku
        assert restored.price == sample_product.price
        assert restored.description == sample_product.description

    def test_from_dict_without_description_defaults_to_empty(
        self, sample_price: Money
    ) -> None:
        data = {
            "id": "abc-123",
            "name": "Widget",
            "sku": "WGT-001",
            "price": {"amount": "5.00", "currency": "EUR"},
        }
        p = Product.from_dict(data)
        assert p.description == ""


class TestProductIdentity:
    def test_same_id_products_are_equal(self, sample_price: Money) -> None:
        """Entity equality is id-only; different field values don't matter."""
        p1 = Product(id="same-id", name="Name A", sku="SKU-A", price=sample_price)
        p2 = Product(id="same-id", name="Name B", sku="SKU-B", price=sample_price)
        assert p1 == p2

    def test_different_id_products_are_not_equal(self, sample_price: Money) -> None:
        p1 = Product(id="id-1", name="Widget", sku="WGT-001", price=sample_price)
        p2 = Product(id="id-2", name="Widget", sku="WGT-001", price=sample_price)
        assert p1 != p2

    def test_product_is_hashable_by_id(self, sample_price: Money) -> None:
        p1 = Product(id="same-id", name="A", sku="A", price=sample_price)
        p2 = Product(id="same-id", name="B", sku="B", price=sample_price)
        product_set = {p1, p2}
        assert len(product_set) == 1
