"""SQLAlchemy ORM models for tax domain."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CustomerModel(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(10))
    tax_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_exempt: Mapped[bool] = mapped_column(default=False)

    orders: Mapped[list[OrderModel]] = relationship(back_populates="customer")


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    order_type: Mapped[str] = mapped_column(String(10))

    customer: Mapped[CustomerModel] = relationship(back_populates="orders")
    items: Mapped[list[OrderItemModel]] = relationship(back_populates="order")


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(12, 4))

    order: Mapped[OrderModel] = relationship(back_populates="items")


class TaxRuleModel(Base):
    __tablename__ = "tax_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country: Mapped[str] = mapped_column(String(10))
    tax_name: Mapped[str] = mapped_column(String(50))
    rate: Mapped[Decimal] = mapped_column(DECIMAL(6, 4))
    description: Mapped[str] = mapped_column(Text, default="")
