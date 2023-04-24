from django.db import models
from django.contrib.auth.models import User
# Create your models here.


def csv_upload_to(instance, filename):
    """Return the path where the CSV file should be uploaded"""
    return f"csv_files/{instance.user.username}/{filename}"


class Csv(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to=csv_upload_to, blank=False)

    def __str__(self):
        return self.csv_file.name
