"""Sample product dataset used by the Streamlit demo."""

from __future__ import annotations

from dashboard_mediator.domain.entities import Product

SAMPLE_PRODUCTS: list[Product] = [
    Product(name="Laptop", category="electronics", price=1200.0),
    Product(name="Headphones", category="electronics", price=150.0),
    Product(name="Desk Lamp", category="home", price=35.0),
    Product(name="Office Chair", category="home", price=220.0),
    Product(name="Novel", category="books", price=18.0),
    Product(name="Cookbook", category="books", price=25.0),
]
