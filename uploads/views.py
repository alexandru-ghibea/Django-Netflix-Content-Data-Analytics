from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from .forms import CsvUploadForm
from django.contrib.auth import get_user_model
from .models import Csv
from django.views.generic import ListView
from .models import Csv
from django.urls import reverse_lazy
from django.core.files.storage import default_storage


# class UploadFileView(LoginRequiredMixin, FormView):
#     template_name = 'uploads/uploads_form.html'
#     form_class = CsvUploadForm
#     success_url = reverse_lazy('uploads:uploads_list')

#     def form_valid(self, form):
#         csv_file = form.cleaned_data.get('csv_file')
#         csv = Csv(user=self.request.user, csv_file=csv_file)
#         csv.save()
#         return super().form_valid(form)


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

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('uploads:uploads_list', kwargs={'username': self.request.user.username})


class UploadFileListView(LoginRequiredMixin, ListView):
    model = Csv
    template_name = 'uploads/uploads_list.html'
    context_object_name = 'csv_list'

    def get_queryset(self):
        queryset = super().get_queryset()
        return Csv.objects.filter(user=self.request.user)
