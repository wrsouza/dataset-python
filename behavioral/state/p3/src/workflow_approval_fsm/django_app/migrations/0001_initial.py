from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="WorkflowRequestModel",
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
                    "request_id",
                    models.CharField(db_index=True, max_length=64, unique=True),
                ),
                ("title", models.CharField(max_length=200)),
                ("state", models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name="NotificationLogModel",
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
                ("request_id", models.CharField(db_index=True, max_length=64)),
                ("message", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField()),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
    ]
