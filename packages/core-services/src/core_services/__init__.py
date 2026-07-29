"""core_services — application services for the product catalog.

This package contains services that orchestrate domain entities and the
Repository protocol. Services live here (rather than in core_domain) because
they depend on the Repository abstraction from framework_core — a
non-domain concern — so they form a separate, higher layer.

Why a separate package from core_domain?
  A downstream application that only needs to query products (e.g. a reporting
  tool) should be able to depend on core_domain without pulling in service-layer
  code. Keeping them apart also makes the dependency graph explicit.
"""

from core_services.product_service import ProductService
from core_services.catalog import CatalogQuery

__all__ = ["ProductService", "CatalogQuery"]
