from django.db import models
from django.contrib.auth.models import User

# Create your models here.


def csv_upload_to(instance, filename):
    """Return the path where the profile picture file should be uploaded"""
    return f"profile_pictures/{instance.user.username}/{filename}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    User._meta.get_field('email')._unique = True
    profile_pic = models.ImageField(upload_to=csv_upload_to)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.username

    def get_profile_pic(self):
        if self.profile_pic and hasattr(self.profile_pic, 'url'):
            return self.profile_pic.url
        else:
            return '/static/images/default_profile_pic.png'
