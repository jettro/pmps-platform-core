"""ProductService — the primary write entry-point for the catalog.

Lives in core_services (not core_domain) because it depends on:
  - framework_core.Repository (infrastructure abstraction)
  - framework_core.Result (application-layer success/failure signalling)

Neither of those belongs in a pure domain model, so the service sits one
layer above, mediating between callers and the domain objects.
"""

from __future__ import annotations

from framework_core import Repository, Result, Success, Failure

from core_domain.money import Money
from core_domain.product import Product


class ProductService:
    """Application service for managing the product catalog.

    Provides create / read / list / delete operations, returning Result types
    for operations that can legitimately fail (add) and plain values for
    operations that cannot (get, list, remove).

    The service is intentionally thin: it delegates persistence to the
    Repository and domain construction to the Product class. Business rules
    that are universal to the domain (e.g. "a product must have a name") are
    enforced here, while rules specific to an application context belong in
    that application's own service layer.

    Args:
        repository: Any Repository[Product] implementation — in-memory for
                    tests, file- or DB-backed in production.
    """

    def __init__(self, repository: Repository[Product]) -> None:
        self._repo = repository

    def add(
        self,
        name: str,
        sku: str,
        price: Money,
        description: str = "",
    ) -> Result[Product, str]:
        """Create and persist a new product.

        Validates basic domain invariants before saving so that invalid
        products never reach the repository.

        Args:
            name:        Human-readable product name (must be non-empty).
            sku:         Stock-keeping unit code (must be non-empty).
            price:       Sale price as a Money value object.
            description: Optional long-form description.

        Returns:
            Success[Product] on success, Failure[str] with a human-readable
            error message if validation fails.
        """
        if not name.strip():
            return Failure("Product name cannot be empty")
        if not sku.strip():
            return Failure("SKU cannot be empty")

        product = Product(name=name, sku=sku, price=price, description=description)
        saved = self._repo.save(product)
        return Success(saved)

    def get(self, id: str) -> Product | None:
        """Retrieve a single product by its unique identifier.

        Returns None rather than raising to keep callers from having to
        handle unnecessary exceptions for a routine "not found" condition.

        Args:
            id: The product's UUID.

        Returns:
            The Product if found, None otherwise.
        """
        return self._repo.get(id)

    def list(self) -> list[Product]:
        """Return every product currently in the catalog.

        Returns:
            A list of Product objects; empty list if the catalog is empty.
        """
        return self._repo.list()

    def remove(self, id: str) -> bool:
        """Remove a product from the catalog.

        Args:
            id: The UUID of the product to remove.

        Returns:
            True if the product existed and was removed, False if not found.
        """
        return self._repo.delete(id)
