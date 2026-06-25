from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UserCredentialModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "username",
                    models.CharField(db_index=True, max_length=100, unique=True),
                ),
                ("password_hash", models.CharField(max_length=255)),
                ("user_id", models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name="ApiTokenModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("token", models.CharField(db_index=True, max_length=128, unique=True)),
                ("user_id", models.CharField(max_length=64)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="OAuthIdentityModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("provider", models.CharField(max_length=50)),
                ("provider_user_id", models.CharField(max_length=100)),
                ("user_id", models.CharField(max_length=64)),
            ],
            options={
                "unique_together": {("provider", "provider_user_id")},
            },
        ),
        migrations.CreateModel(
            name="AuthAttemptLogModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("strategy_name", models.CharField(max_length=50)),
                ("success", models.BooleanField()),
                ("user_id", models.CharField(blank=True, max_length=64, null=True)),
                ("reason", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField()),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
    ]
