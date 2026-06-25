"""Django ORM models backing the three authentication strategies."""

from __future__ import annotations

from django.db import models


class UserCredentialModel(models.Model):
    """Backs PasswordAuthStrategy — username + hashed password."""

    objects: models.Manager[UserCredentialModel]

    username = models.CharField(max_length=100, unique=True, db_index=True)
    password_hash = models.CharField(max_length=255)
    user_id = models.CharField(max_length=64)

    def __str__(self) -> str:
        return self.username


class ApiTokenModel(models.Model):
    """Backs TokenAuthStrategy — a static bearer token per user."""

    objects: models.Manager[ApiTokenModel]

    token = models.CharField(max_length=128, unique=True, db_index=True)
    user_id = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.token


class OAuthIdentityModel(models.Model):
    """Backs OAuthStrategy — maps a provider's user id to a local user_id."""

    objects: models.Manager[OAuthIdentityModel]

    provider = models.CharField(max_length=50)
    provider_user_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=64)

    class Meta:
        unique_together = [("provider", "provider_user_id")]

    def __str__(self) -> str:
        return f"{self.provider}:{self.provider_user_id}"


class AuthAttemptLogModel(models.Model):
    """One row per authentication attempt, regardless of outcome."""

    objects: models.Manager[AuthAttemptLogModel]

    strategy_name = models.CharField(max_length=50)
    success = models.BooleanField()
    user_id = models.CharField(max_length=64, null=True, blank=True)
    reason = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        ordering = ["created_at"]
