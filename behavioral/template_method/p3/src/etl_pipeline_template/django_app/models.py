"""Django ORM models: staging tables (raw input) and target tables
(transformed output) for the two ETL pipelines."""

from __future__ import annotations

from django.db import models


class CustomerStagingModel(models.Model):
    """Raw, untransformed customer records (e.g. dropped by an upstream system)."""

    objects: models.Manager[CustomerStagingModel]

    source_id = models.CharField(max_length=64, unique=True, db_index=True)
    full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)


class CustomerModel(models.Model):
    """Transformed, loaded customer record."""

    objects: models.Manager[CustomerModel]

    source_id = models.CharField(max_length=64, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=200)


class OrderStagingModel(models.Model):
    """Raw, untransformed order records."""

    objects: models.Manager[OrderStagingModel]

    source_id = models.CharField(max_length=64, unique=True, db_index=True)
    unit_price = models.FloatField()
    quantity = models.IntegerField()


class OrderModel(models.Model):
    """Transformed, loaded order record — quantity * price pre-computed."""

    objects: models.Manager[OrderModel]

    source_id = models.CharField(max_length=64, unique=True, db_index=True)
    total = models.FloatField()
