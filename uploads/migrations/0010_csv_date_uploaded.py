# Generated by Django 4.1.7 on 2023-04-24 12:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("uploads", "0009_remove_csv_date_uploaded_remove_csv_file_csv_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="csv",
            name="date_uploaded",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
