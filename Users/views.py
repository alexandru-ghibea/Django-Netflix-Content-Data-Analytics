from . import forms
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from .models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
# Create your views here.

User = get_user_model()


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


class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'users/profile_detail.html'
    model = UserProfile

    def get_object(self):
        # Retrieve the User object for the currently logged-in user
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        context['user_profile'] = user_profile
        return context


class ChangeProfilePictureView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    fields = ['profile_pic']
    template_name = 'users/change_profile_picture.html'

    def get_object(self):
        # Retrieve the User object for the currently logged-in user
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        context['user_profile'] = user_profile
        return context

    def form_valid(self, form):
        profile_pic = form.cleaned_data.get('profile_pic')
        if profile_pic:
            user_profile = UserProfile.objects.get(user=self.request.user)
            user_profile.profile_pic = profile_pic
            user_profile.save()
        return redirect('users:profile_detail', pk=self.request.user.pk)
