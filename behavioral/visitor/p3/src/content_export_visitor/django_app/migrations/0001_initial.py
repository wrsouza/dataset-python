from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ExportJobModel",
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
                ("job_id", models.CharField(db_index=True, max_length=64, unique=True)),
                ("format_name", models.CharField(max_length=20)),
                ("s3_key", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField()),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
