from __future__ import annotations

import logging
from uuid import uuid4

from src.order.domain.entities import Cart, Customer, Order, ShippingLabel

logger = logging.getLogger(__name__)

BASE_SHIPPING_COST = 9.99
FREE_SHIPPING_THRESHOLD = 100.0


class MockShippingService:
    """
    Mock shipping service that simulates carrier integration.

    Calculates shipping based on order total and generates tracking numbers.
    Orders above the free shipping threshold get zero cost shipping.
    """

    def calculate_shipping(self, customer: Customer, cart: Cart) -> ShippingLabel:
        shipping_cost = (
            0.0 if cart.total >= FREE_SHIPPING_THRESHOLD else BASE_SHIPPING_COST
        )
        carrier = "FastShip"
        estimated_days = 3

        logger.info(
            "Calculated shipping for customer %s: $%.2f via %s",
            customer.id,
            shipping_cost,
            carrier,
        )

        return ShippingLabel(
            tracking_number="",
            carrier=carrier,
            estimated_days=estimated_days,
            shipping_cost=shipping_cost,
        )

    def generate_label(self, order: Order, label: ShippingLabel) -> ShippingLabel:
        tracking_number = f"FS{uuid4().hex[:12].upper()}"
        logger.info("Generated label %s for order %s", tracking_number, order.id)

        return ShippingLabel(
            tracking_number=tracking_number,
            carrier=label.carrier,
            estimated_days=label.estimated_days,
            shipping_cost=label.shipping_cost,
        )
