# Generated by Django 4.0.5 on 2022-06-17 13:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0002_remove_image_thumbnail"),
    ]

    operations = [
        migrations.RenameField(
            model_name="image",
            old_name="image",
            new_name="original_image",
        ),
    ]
