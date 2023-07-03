from django.urls import path
from . import views
app_name = 'analytics'

urlpatterns = [
    path('analytics/<str:filename>',
         views.CsvAnalyticsView.as_view(), name='csv_analytics'),
]
