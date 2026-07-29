"""Postal address value object.

Addresses are value objects: two addresses with identical fields are
considered equal regardless of object identity. Frozen ensures they cannot
be accidentally mutated once attached to an order or customer record.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    """An immutable postal address.

    Intentionally free of any validation logic — domain rules about which
    country codes are valid or how postal codes are formatted belong in
    application or domain services, not in the value object itself.

    Args:
        street: Street name and number (e.g. "123 Main St").
        city: City or locality name.
        country: ISO-3166-1 alpha-2 country code (e.g. "NL", "DE").
        postal_code: Postal / ZIP code in the format appropriate for the country.
    """

    street: str
    city: str
    country: str
    postal_code: str
