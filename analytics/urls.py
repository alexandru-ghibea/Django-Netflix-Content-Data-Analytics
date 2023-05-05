from django.urls import path
from . import views
app_name = 'analytics'

urlpatterns = [
    path('profiles/<str:filename>',
         views.CsvProfileView.as_view(), name='profile_list'),
]
