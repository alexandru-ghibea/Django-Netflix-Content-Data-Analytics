from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile_detail/<int:pk>/',
         views.ProfileDetailView.as_view(), name='profile_detail'),
    path('change_profile_picture/', views.ChangeProfilePictureView.as_view(),
         name='change_profile_picture')

]
