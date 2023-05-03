from django import views
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = 'home_page.html'


class LoginSuccess(TemplateView):
    template_name = 'login_success.html'


class LogoutSuccess(TemplateView):
    template_name = 'logout_success.html'

