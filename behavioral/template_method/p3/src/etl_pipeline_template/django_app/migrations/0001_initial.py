from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CustomerStagingModel",
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
                    "source_id",
                    models.CharField(db_index=True, max_length=64, unique=True),
                ),
                ("full_name", models.CharField(max_length=200)),
                ("email", models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name="CustomerModel",
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
                    "source_id",
                    models.CharField(db_index=True, max_length=64, unique=True),
                ),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("email", models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name="OrderStagingModel",
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
                    "source_id",
                    models.CharField(db_index=True, max_length=64, unique=True),
                ),
                ("unit_price", models.FloatField()),
                ("quantity", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="OrderModel",
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
                    "source_id",
                    models.CharField(db_index=True, max_length=64, unique=True),
                ),
                ("total", models.FloatField()),
            ],
        ),
    ]
