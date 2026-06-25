"""ConcreteSubject: Kafka-backed price monitor.

Publishes PriceEvents to a Kafka topic; a background consumer thread
deserialises messages and fans out to registered local observers.
"""

from __future__ import annotations

import json
import logging
import threading
import uuid
from collections import defaultdict
from typing import TYPE_CHECKING

from price_alerts.domain.entities import PriceEvent, Subscription
from price_alerts.domain.interfaces import PriceMonitor, PriceObserver

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

TOPIC_NAME = "price-changes"


class KafkaPriceMonitor(PriceMonitor):
    """ConcreteSubject: uses Kafka for event distribution.

    - `notify_price_change` serialises to JSON and publishes to Kafka.
    - A consumer thread reads the topic and dispatches to local observers.
    - Subscriptions are stored in-memory (DIP: no direct DB dependency).
    """

    def __init__(self, kafka_bootstrap: str) -> None:
        self._kafka_bootstrap = kafka_bootstrap
        # subscription_id -> Subscription
        self._subscriptions: dict[str, Subscription] = {}
        # observer_id -> PriceObserver
        self._observers: dict[str, PriceObserver] = {}
        # product_id -> list[subscription_id]
        self._product_index: dict[str, list[str]] = defaultdict(list)
        self._lock = threading.Lock()
        self._consumer_thread: threading.Thread | None = None
        self._running = False

    # ── Subject interface ────────────────────────────────────────────────────

    def subscribe(
        self,
        observer: PriceObserver,
        product_id: str,
        threshold: float,
    ) -> str:
        sub_id = str(uuid.uuid4())
        sub = Subscription(
            subscription_id=sub_id,
            observer_id=observer.observer_id,
            product_id=product_id,
            threshold=threshold,
        )
        with self._lock:
            self._subscriptions[sub_id] = sub
            self._observers[observer.observer_id] = observer
            self._product_index[product_id].append(sub_id)
        logger.info(
            "Subscribed %s to %s (threshold %.1f%%)",
            observer.observer_id,
            product_id,
            threshold,
        )
        return sub_id

    def unsubscribe(self, subscription_id: str) -> None:
        with self._lock:
            sub = self._subscriptions.pop(subscription_id, None)
            if sub is None:
                return
            product_subs = self._product_index.get(sub.product_id)
            if product_subs and subscription_id in product_subs:
                product_subs.remove(subscription_id)
            still_referenced = any(
                other.observer_id == sub.observer_id
                for other in self._subscriptions.values()
            )
            if not still_referenced:
                self._observers.pop(sub.observer_id, None)
            logger.info("Unsubscribed %s from %s", sub.observer_id, sub.product_id)

    def notify_price_change(
        self,
        product_id: str,
        old_price: float,
        new_price: float,
    ) -> None:
        event = PriceEvent.from_prices(product_id, old_price, new_price)
        # Publish to Kafka (best-effort; falls back to direct fan-out if unavailable)
        published = self._publish_to_kafka(event)
        if not published:
            # Direct fan-out when Kafka is not available (e.g. tests)
            self._fan_out(event)

    def _publish_to_kafka(self, event: PriceEvent) -> bool:
        try:
            from kafka import KafkaProducer

            producer = KafkaProducer(
                bootstrap_servers=self._kafka_bootstrap,
                value_serializer=lambda v: json.dumps(v).encode(),
            )
            producer.send(
                TOPIC_NAME,
                value={
                    "product_id": event.product_id,
                    "old_price": event.old_price,
                    "new_price": event.new_price,
                    "change_pct": event.change_pct,
                    "timestamp": event.timestamp.isoformat(),
                },
            )
            producer.flush()
            producer.close()
            return True
        except Exception as exc:
            logger.warning("Kafka unavailable (%s); using direct fan-out", exc)
            return False

    def _fan_out(self, event: PriceEvent) -> None:
        """Dispatch event to all matching local observers (direct path)."""
        with self._lock:
            sub_ids = list(self._product_index.get(event.product_id, []))

        for sub_id in sub_ids:
            sub = self._subscriptions.get(sub_id)
            if sub is None or not sub.is_active:
                continue
            if not event.exceeds_threshold(sub.threshold):
                continue
            observer = self._observers.get(sub.observer_id)
            if observer:
                try:
                    observer.on_price_change(event)
                except Exception:
                    logger.exception("Observer %s failed", sub.observer_id)

    # ── Kafka consumer ───────────────────────────────────────────────────────

    def start_consumer(self) -> None:
        self._running = True
        self._consumer_thread = threading.Thread(target=self._consume_loop, daemon=True)
        self._consumer_thread.start()

    def stop_consumer(self) -> None:
        self._running = False

    def _consume_loop(self) -> None:
        try:
            from kafka import KafkaConsumer

            consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=self._kafka_bootstrap,
                auto_offset_reset="latest",
                value_deserializer=lambda m: json.loads(m.decode()),
            )
            for message in consumer:
                if not self._running:
                    break
                data = message.value
                event = PriceEvent(
                    product_id=data["product_id"],
                    old_price=data["old_price"],
                    new_price=data["new_price"],
                    change_pct=data["change_pct"],
                )
                self._fan_out(event)
        except Exception:
            logger.exception("Kafka consumer error")

    @property
    def subscriptions(self) -> dict[str, Subscription]:
        return dict(self._subscriptions)
