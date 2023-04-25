from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from uploads.views import UploadFileListView
app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile_detail/',
         views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile_detail/change_picture/',
         views.ProfileUpdateView.as_view(), name='profile_update'),
]
