"""CatalogQuery — read-only query façade over the product catalog.

Separating reads (CatalogQuery) from writes (ProductService) follows the
CQRS principle: query and command paths have different concerns, different
caching strategies, and different authorisation rules. Keeping them in
separate classes makes those differences explicit.

CatalogQuery lives in core_services (not core_domain) because it wraps
ProductService, which is already at the service layer. A domain model
should not depend on a service.
"""

from __future__ import annotations

from core_domain.product import Product
from core_services.product_service import ProductService


class CatalogQuery:
    """Read-only query façade over the product catalog.

    All methods are pure reads — they never modify state. Callers that only
    need to browse or filter products can depend on CatalogQuery without
    gaining access to mutation methods.

    Args:
        service: A ProductService instance to delegate list operations to.
                 Using ProductService (rather than going directly to the
                 repository) ensures that any caching or access-control logic
                 in the service is consistently applied.
    """

    def __init__(self, service: ProductService) -> None:
        self._service = service

    def search(self, query: str) -> list[Product]:
        """Find products whose name or SKU contains the query string.

        The search is case-insensitive and uses substring matching, so
        "widget" matches "Blue Widget" and "WIDGET-001".

        Args:
            query: The search term; empty string returns all products.

        Returns:
            A (potentially empty) list of matching Product objects.
        """
        lower = query.lower()
        return [
            p
            for p in self._service.list()
            if lower in p.name.lower() or lower in p.sku.lower()
        ]

    def by_currency(self, currency: str) -> list[Product]:
        """Return all products whose price is denominated in the given currency.

        Useful for region-specific catalog views where only EUR or USD
        products should be displayed.

        Args:
            currency: An ISO-4217 currency code, e.g. "EUR", "USD".
                      Comparison is exact (not case-normalised), so callers
                      should pass the canonical uppercase code.

        Returns:
            A (potentially empty) list of Product objects priced in that currency.
        """
        return [p for p in self._service.list() if p.price.currency == currency]
