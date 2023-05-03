from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from uploads.models import Csv
import os
from django.utils import timezone
# Create your views here.


# class ForAnalyticsListView(LoginRequiredMixin, ListView):
#     model = Csv
#     template_name = 'analytics/all_filles.html'
#     context_object_name = 'csv_list'

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         queryset = queryset.filter(user=self.request.user)
#         file_list = []
#         for csv in queryset:
#             filename = os.path.basename(csv.csv_file.path)
#             date_uploaded = timezone.localtime(
#                 csv.date_uploaded).strftime("%B %d, %Y, %I:%M %p")
#             file_list.append(
#                 {'filename': filename, 'date_uploaded': date_uploaded})
#         return file_list
