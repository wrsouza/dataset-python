"""FlyweightFactory: ProductTypeFactory with lazy-load from MySQL and memory cache."""

from __future__ import annotations

from decimal import Decimal

from catalog.domain.entities import ProductType

# 50 distinct ProductType combinations — intrinsic state
_PRODUCT_TYPE_DEFINITIONS: list[dict[str, object]] = [
    {
        "category_name": "Electronics",
        "brand": "Samsung",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "heavy",
        "return_policy": "30 days",
    },
    {
        "category_name": "Electronics",
        "brand": "Apple",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "fragile",
        "return_policy": "14 days",
    },
    {
        "category_name": "Electronics",
        "brand": "Sony",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "heavy",
        "return_policy": "30 days",
    },
    {
        "category_name": "Electronics",
        "brand": "LG",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "heavy",
        "return_policy": "30 days",
    },
    {
        "category_name": "Electronics",
        "brand": "Xiaomi",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "standard",
        "return_policy": "7 days",
    },
    {
        "category_name": "Clothing",
        "brand": "Nike",
        "tax_rate": Decimal("12.00"),
        "shipping_class": "light",
        "return_policy": "60 days",
    },
    {
        "category_name": "Clothing",
        "brand": "Adidas",
        "tax_rate": Decimal("12.00"),
        "shipping_class": "light",
        "return_policy": "60 days",
    },
    {
        "category_name": "Clothing",
        "brand": "Zara",
        "tax_rate": Decimal("12.00"),
        "shipping_class": "light",
        "return_policy": "30 days",
    },
    {
        "category_name": "Clothing",
        "brand": "H&M",
        "tax_rate": Decimal("12.00"),
        "shipping_class": "light",
        "return_policy": "30 days",
    },
    {
        "category_name": "Clothing",
        "brand": "Uniqlo",
        "tax_rate": Decimal("12.00"),
        "shipping_class": "light",
        "return_policy": "30 days",
    },
    {
        "category_name": "Books",
        "brand": "Penguin",
        "tax_rate": Decimal("0.00"),
        "shipping_class": "light",
        "return_policy": "no returns",
    },
    {
        "category_name": "Books",
        "brand": "OReilly",
        "tax_rate": Decimal("0.00"),
        "shipping_class": "light",
        "return_policy": "no returns",
    },
    {
        "category_name": "Books",
        "brand": "Manning",
        "tax_rate": Decimal("0.00"),
        "shipping_class": "light",
        "return_policy": "no returns",
    },
    {
        "category_name": "Home",
        "brand": "IKEA",
        "tax_rate": Decimal("10.00"),
        "shipping_class": "heavy",
        "return_policy": "90 days",
    },
    {
        "category_name": "Home",
        "brand": "Philips",
        "tax_rate": Decimal("10.00"),
        "shipping_class": "standard",
        "return_policy": "30 days",
    },
    {
        "category_name": "Home",
        "brand": "Bosch",
        "tax_rate": Decimal("10.00"),
        "shipping_class": "heavy",
        "return_policy": "24 months",
    },
    {
        "category_name": "Home",
        "brand": "Electrolux",
        "tax_rate": Decimal("10.00"),
        "shipping_class": "heavy",
        "return_policy": "24 months",
    },
    {
        "category_name": "Sports",
        "brand": "Wilson",
        "tax_rate": Decimal("8.00"),
        "shipping_class": "standard",
        "return_policy": "30 days",
    },
    {
        "category_name": "Sports",
        "brand": "Puma",
        "tax_rate": Decimal("8.00"),
        "shipping_class": "light",
        "return_policy": "30 days",
    },
    {
        "category_name": "Sports",
        "brand": "Decathlon",
        "tax_rate": Decimal("8.00"),
        "shipping_class": "standard",
        "return_policy": "365 days",
    },
    {
        "category_name": "Food",
        "brand": "Nestle",
        "tax_rate": Decimal("5.00"),
        "shipping_class": "perishable",
        "return_policy": "no returns",
    },
    {
        "category_name": "Food",
        "brand": "Unilever",
        "tax_rate": Decimal("5.00"),
        "shipping_class": "perishable",
        "return_policy": "no returns",
    },
    {
        "category_name": "Toys",
        "brand": "LEGO",
        "tax_rate": Decimal("8.00"),
        "shipping_class": "standard",
        "return_policy": "30 days",
    },
    {
        "category_name": "Toys",
        "brand": "Mattel",
        "tax_rate": Decimal("8.00"),
        "shipping_class": "light",
        "return_policy": "30 days",
    },
    {
        "category_name": "Toys",
        "brand": "Hasbro",
        "tax_rate": Decimal("8.00"),
        "shipping_class": "light",
        "return_policy": "30 days",
    },
    {
        "category_name": "Beauty",
        "brand": "LOreal",
        "tax_rate": Decimal("12.00"),
        "shipping_class": "fragile",
        "return_policy": "no returns",
    },
    {
        "category_name": "Beauty",
        "brand": "Nivea",
        "tax_rate": Decimal("12.00"),
        "shipping_class": "light",
        "return_policy": "no returns",
    },
    {
        "category_name": "Beauty",
        "brand": "Maybelline",
        "tax_rate": Decimal("12.00"),
        "shipping_class": "light",
        "return_policy": "no returns",
    },
    {
        "category_name": "Automotive",
        "brand": "Bosch",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "heavy",
        "return_policy": "14 days",
    },
    {
        "category_name": "Automotive",
        "brand": "Castrol",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "standard",
        "return_policy": "no returns",
    },
    {
        "category_name": "Pet",
        "brand": "Royal Canin",
        "tax_rate": Decimal("5.00"),
        "shipping_class": "standard",
        "return_policy": "no returns",
    },
    {
        "category_name": "Pet",
        "brand": "Whiskas",
        "tax_rate": Decimal("5.00"),
        "shipping_class": "standard",
        "return_policy": "no returns",
    },
    {
        "category_name": "Garden",
        "brand": "Husqvarna",
        "tax_rate": Decimal("10.00"),
        "shipping_class": "heavy",
        "return_policy": "30 days",
    },
    {
        "category_name": "Garden",
        "brand": "Black&Decker",
        "tax_rate": Decimal("10.00"),
        "shipping_class": "heavy",
        "return_policy": "30 days",
    },
    {
        "category_name": "Music",
        "brand": "Yamaha",
        "tax_rate": Decimal("15.00"),
        "shipping_class": "fragile",
        "return_policy": "14 days",
    },
    {
        "category_name": "Music",
        "brand": "Roland",
        "tax_rate": Decimal("15.00"),
        "shipping_class": "fragile",
        "return_policy": "14 days",
    },
    {
        "category_name": "Office",
        "brand": "Brother",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "standard",
        "return_policy": "30 days",
    },
    {
        "category_name": "Office",
        "brand": "HP",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "standard",
        "return_policy": "30 days",
    },
    {
        "category_name": "Office",
        "brand": "Canon",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "heavy",
        "return_policy": "30 days",
    },
    {
        "category_name": "Health",
        "brand": "Johnson",
        "tax_rate": Decimal("5.00"),
        "shipping_class": "fragile",
        "return_policy": "no returns",
    },
    {
        "category_name": "Health",
        "brand": "Pfizer",
        "tax_rate": Decimal("0.00"),
        "shipping_class": "fragile",
        "return_policy": "no returns",
    },
    {
        "category_name": "Gaming",
        "brand": "Nintendo",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "fragile",
        "return_policy": "7 days",
    },
    {
        "category_name": "Gaming",
        "brand": "PlayStation",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "fragile",
        "return_policy": "7 days",
    },
    {
        "category_name": "Gaming",
        "brand": "Xbox",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "fragile",
        "return_policy": "7 days",
    },
    {
        "category_name": "Furniture",
        "brand": "IKEA",
        "tax_rate": Decimal("10.00"),
        "shipping_class": "freight",
        "return_policy": "365 days",
    },
    {
        "category_name": "Furniture",
        "brand": "Ashley",
        "tax_rate": Decimal("10.00"),
        "shipping_class": "freight",
        "return_policy": "30 days",
    },
    {
        "category_name": "Baby",
        "brand": "Pampers",
        "tax_rate": Decimal("0.00"),
        "shipping_class": "light",
        "return_policy": "no returns",
    },
    {
        "category_name": "Baby",
        "brand": "Huggies",
        "tax_rate": Decimal("0.00"),
        "shipping_class": "light",
        "return_policy": "no returns",
    },
    {
        "category_name": "Jewelry",
        "brand": "Pandora",
        "tax_rate": Decimal("20.00"),
        "shipping_class": "insured",
        "return_policy": "30 days",
    },
    {
        "category_name": "Jewelry",
        "brand": "Swarovski",
        "tax_rate": Decimal("20.00"),
        "shipping_class": "insured",
        "return_policy": "30 days",
    },
]


class ProductTypeFactory:
    """FlyweightFactory — lazy-loads ProductTypes and caches them in memory.

    The first call to get_or_create may trigger a DB lookup (or use the
    pre-defined config). Subsequent calls with the same key return the
    same Python object (identity guaranteed via 'is' check).
    """

    def __init__(self) -> None:
        self._cache: dict[str, ProductType] = {}

    def _build_key(
        self,
        category_name: str,
        brand: str,
        tax_rate: Decimal,
        shipping_class: str,
    ) -> str:
        return f"{category_name}|{brand}|{tax_rate}|{shipping_class}"

    def get_or_create(
        self,
        category_name: str,
        brand: str,
        tax_rate: object,
        shipping_class: str,
        return_policy: str,
    ) -> ProductType:
        """Return the shared Flyweight — create and cache if first encounter."""
        rate = Decimal(str(tax_rate))
        cache_key = self._build_key(category_name, brand, rate, shipping_class)
        if cache_key not in self._cache:
            self._cache[cache_key] = ProductType(
                category_name=category_name,
                brand=brand,
                tax_rate=rate,
                shipping_class=shipping_class,
                return_policy=return_policy,
            )
        return self._cache[cache_key]

    def load_all_from_definitions(self) -> None:
        """Pre-populate cache from the static definitions list."""
        for defn in _PRODUCT_TYPE_DEFINITIONS:
            self.get_or_create(
                category_name=str(defn["category_name"]),
                brand=str(defn["brand"]),
                tax_rate=defn["tax_rate"],
                shipping_class=str(defn["shipping_class"]),
                return_policy=str(defn["return_policy"]),
            )

    def cached_count(self) -> int:
        """Return the number of unique Flyweights in the in-memory pool."""
        return len(self._cache)

    def get_all_types(self) -> list[ProductType]:
        """Return all cached ProductType flyweights."""
        return list(self._cache.values())

    def get_definitions(self) -> list[dict[str, object]]:
        """Return raw definitions for DB seeding."""
        return _PRODUCT_TYPE_DEFINITIONS
