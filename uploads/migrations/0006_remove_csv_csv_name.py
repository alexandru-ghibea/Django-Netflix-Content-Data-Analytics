# Generated by Django 4.1.7 on 2023-04-22 09:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("uploads", "0005_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="csv",
            name="csv_name",
        ),
    ]
