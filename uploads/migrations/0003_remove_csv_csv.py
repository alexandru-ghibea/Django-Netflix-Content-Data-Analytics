# Generated by Django 4.1.7 on 2023-04-22 09:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("uploads", "0002_rename_user_csv_csv"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="csv",
            name="csv",
        ),
    ]
