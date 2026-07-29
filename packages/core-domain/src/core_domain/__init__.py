"""core_domain — shared domain primitives for the product catalog.

This package contains value objects (Money, Address) and the Product entity
shared across all applications in this project. It intentionally contains NO
application logic — only the domain model.

Why a separate package?
  Domain primitives change rarely and must be consistent everywhere. Isolating
  them here lets sales-application and any future app depend on exactly this
  version without pulling in application-level code.
"""

from core_domain.money import Money
from core_domain.address import Address
from core_domain.product import Product

__all__ = ["Money", "Address", "Product"]
