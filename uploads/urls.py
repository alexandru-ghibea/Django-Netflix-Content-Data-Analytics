from django.urls import path
from .views import UploadFileListView, UploadFileView
app_name = 'uploads'

urlpatterns = [
    path('csv_upload', UploadFileView.as_view(), name='csv_upload'),
    path('all_filles/', UploadFileListView.as_view(), name='all_filles'),

]
