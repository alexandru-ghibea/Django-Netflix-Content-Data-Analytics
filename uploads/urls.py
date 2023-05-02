from django.urls import path
from .views import UploadFileView, UploadFileListView
app_name = 'uploads'

urlpatterns = [
    path('csv_upload', UploadFileView.as_view(), name='csv_upload'),
    path('<username>', UploadFileListView.as_view(), name='uploads_list'),


]
