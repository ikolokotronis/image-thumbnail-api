# Generated by Django 4.0.5 on 2022-06-20 13:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import images.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("images", "0004_image_expiration_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="original_image",
            field=models.ImageField(upload_to=images.models.image_upload_location),
        ),
        migrations.CreateModel(
            name="ExpiringImage",
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
                    "image",
                    models.ImageField(
                        upload_to=images.models.expiring_image_upload_location
                    ),
                ),
                ("live_seconds", models.IntegerField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
