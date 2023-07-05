from . import forms
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from .models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.shortcuts import redirect
from django.views.generic import FormView
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail

# Create your views here.

User = get_user_model()


class SignUpView(CreateView):
    form_class = forms.UserRegisterForm
    success_url = reverse_lazy('login')
    template_name = 'users/signup.html'
    # save upload profile pic

    def form_valid(self, form):
        # Get the User object created by the form
        user = form.save()

        # Create a new UserProfile object and set its user attribute
        user_profile = UserProfile.objects.create(user=user)

        # Try to get the profile_pic attribute from the form data
        profile_pic = form.cleaned_data.get('profile_pic')

        # If a profile_pic was uploaded, set it on the UserProfile object
        # Otherwise, set a default value such as an empty string
        if profile_pic:
            user_profile.profile_pic = profile_pic
        else:
            user_profile.profile_pic = ''

        # Save the UserProfile object
        user_profile.save()

        # Call the parent class's form_valid method to save the User object
        return super().form_valid(form)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'users/profile_detail.html'
    model = UserProfile

    def get_object(self):
        # Retrieve the User object for the currently logged-in user
        return UserProfile.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        context['user_profile'] = user_profile
        context['user_timezone'] = timezone.get_current_timezone_name()

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


class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = 'users/change_password.html'
    form_class = forms.PasswordChangeForm
    success_url = reverse_lazy('users:change_password')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, 'Your password was successfully updated!')
        update_session_auth_hash(self.request, form.user)
        return redirect('users:change_password', pk=self.request.user.pk)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ContactView(LoginRequiredMixin, FormView):
    template_name = 'users/contact.html'
    form_class = forms.ContactForm
    success_url = reverse_lazy('users:contact')

    def form_valid(self, form):
        form.send_email()
        messages.success(
            self.request, 'Your message was successfully sent!')
        # return redirect('users:contact')
        return super().form_valid(form)
