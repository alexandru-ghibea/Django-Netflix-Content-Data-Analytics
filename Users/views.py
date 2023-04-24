from django.shortcuts import render
from . import forms
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import UserProfile
# Create your views here.


class SignUpView(CreateView):
    form_class = forms.UserRegisterForm
    success_url = reverse_lazy('login')
    template_name = 'users/signup.html'
    # save upload profile pic

    def form_valid(self, form):
        profile_pic = form.cleaned_data.get('profile_pic')
        if profile_pic:
            user_profile = UserProfile.objects.create(
                user=form.save(), profile_pic=profile_pic)
            user_profile.save()
        return super().form_valid(form)

     