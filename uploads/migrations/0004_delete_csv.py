# Generated by Django 4.1.7 on 2023-04-22 09:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("uploads", "0003_remove_csv_csv"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Csv",
        ),
    ]
