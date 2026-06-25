from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProductModel",
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
                    "product_id",
                    models.CharField(db_index=True, max_length=64, unique=True),
                ),
                ("name", models.CharField(max_length=200)),
                ("price", models.FloatField()),
                ("stock", models.IntegerField()),
                ("current_version", models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name="AuditRecordModel",
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
                ("product_id", models.CharField(db_index=True, max_length=64)),
                ("version", models.IntegerField()),
                ("name", models.CharField(max_length=200)),
                ("price", models.FloatField()),
                ("stock", models.IntegerField()),
                ("changed_by", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField()),
            ],
            options={
                "ordering": ["product_id", "version"],
                "unique_together": {("product_id", "version")},
            },
        ),
    ]
