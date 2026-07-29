"""Product catalog entity.

Product is the central aggregate of this bounded context. It inherits identity
(id, __eq__, __hash__ on id) from framework_core.Entity so it can be stored in
any Repository[Product] implementation.

Why eq=False on the @dataclass decorator?
  Entity manually defines __eq__ and __hash__ based on id only. Using @dataclass
  with eq=True (the default) on a subclass would generate a new __eq__ that
  compares ALL fields, silently overriding the identity semantics. eq=False
  tells the dataclass machinery to leave equality alone so we inherit Entity's
  correct behaviour.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from framework_core import Entity

from core_domain.money import Money


@dataclass(eq=False)
class Product(Entity):
    """A product available in the catalog.

    Attributes:
        id:          UUID assigned by Entity (auto-generated if not supplied).
        name:        Human-readable product name.
        sku:         Stock-keeping unit — unique identifier used by warehouses.
        price:       Sale price as a Money value object.
        description: Optional long-form product description.
    """

    name: str = ""
    sku: str = ""
    price: Money = field(default_factory=lambda: Money(Decimal("0"), "EUR"))
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize the product to a JSON-compatible dictionary.

        Money is expanded to a nested dict so that repositories (e.g.
        JsonFileRepository) can round-trip the value without knowing about
        the Money type.

        Returns:
            A plain dict with all fields, money represented as
            {"amount": str, "currency": str}.
        """
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "price": {
                "amount": str(self.price.amount),
                "currency": self.price.currency,
            },
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Product:
        """Reconstruct a Product from a serialized dict.

        Counterpart to to_dict(); used by repositories when loading persisted
        data back into domain objects.

        Args:
            data: A dict in the format produced by to_dict().

        Returns:
            A fully-populated Product instance with the original id.
        """
        price_data = data["price"]
        return cls(
            id=data["id"],
            name=data["name"],
            sku=data["sku"],
            price=Money(Decimal(price_data["amount"]), price_data["currency"]),
            description=data.get("description", ""),
        )
