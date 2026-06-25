"""Django ORM models for orders and the two independent observer logs."""

from __future__ import annotations

from django.db import models


class OrderModel(models.Model):
    """Current state of an order."""

    objects: models.Manager[OrderModel]

    order_id = models.CharField(max_length=64, unique=True, db_index=True)
    total = models.FloatField()
    status = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"{self.order_id} ({self.status})"


class AuditLogEntryModel(models.Model):
    """Written by AuditLogObserver — one row per order event, for compliance."""

    objects: models.Manager[AuditLogEntryModel]

    order_id = models.CharField(max_length=64, db_index=True)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    class Meta:
        ordering = ["created_at"]


class NotificationLogModel(models.Model):
    """Written by NotificationObserver — one row per channel notified."""

    objects: models.Manager[NotificationLogModel]

    order_id = models.CharField(max_length=64, db_index=True)
    channel = models.CharField(max_length=20)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    class Meta:
        ordering = ["created_at"]
