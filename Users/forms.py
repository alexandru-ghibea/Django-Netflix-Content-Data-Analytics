from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import PasswordChangeForm


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


class ChangeProfilePictureForm(forms.ModelForm):
    """Form for updating profile picture"""
    class Meta:
        model = get_user_model()
        fields = '__all__'


class PasswordChangeForm(PasswordChangeForm):
    """Form for updating password"""

    old_password = forms.CharField(
        label='Old Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


class ContactForm(forms.Form):
    """Form for contacting the website admin"""
    name = forms.CharField(
        label='Your Name',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        label='Your Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    message = forms.CharField(
        label='Your Message',
        widget=forms.Textarea(attrs={'class': 'form-control'}))
