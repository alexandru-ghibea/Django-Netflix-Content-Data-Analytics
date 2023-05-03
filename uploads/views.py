from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from .forms import CsvUploadForm
from django.contrib.auth import get_user_model
from .models import Csv
from django.views.generic import ListView
from .models import Csv
from django.urls import reverse_lazy
from django.core.files.storage import default_storage
from django.utils import timezone
import os
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# from django.contrib import messages


class UploadFileView(LoginRequiredMixin, FormView):
    template_name = 'uploads/uploads_form.html'
    form_class = CsvUploadForm

    def form_valid(self, form):
        csv_file = form.cleaned_data.get('csv_file')
        file_name = csv_file.name
        file_path = f'csv_files/{self.request.user}/{file_name}'

        # Overwrite the file if it already exists
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        # Save the file
        default_storage.save(file_path, csv_file)

        # Create the Csv object
        csv = Csv(user=self.request.user, csv_file=file_path)
        csv.save()
        messages.success(self.request, 'File uploaded successfully')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('uploads:all_filles')


class UploadFileListView(LoginRequiredMixin, ListView):
    model = Csv
    template_name = 'uploads/all_filles.html'
    context_object_name = 'csv_list'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        file_list = []
        for csv in queryset:
            filename = os.path.basename(csv.csv_file.path)
            date_uploaded = timezone.localtime(
                csv.date_uploaded).strftime("%B %d, %Y, %I:%M %p")
            file_list.append(
                {'filename': filename, 'date_uploaded': date_uploaded})
        return file_list
