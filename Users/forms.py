from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms



class UserRegisterForm(UserCreationForm):
    """Form for creating new users for the website"""
    # additional fields for them form
    profile_pic = forms.ImageField(required=False)

    class Meta:
        fields = ('username', 'email', 'password1',
                  'password2', "first_name", "last_name")
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Display Name'
        self.fields['email'].label = 'Email Address'
    