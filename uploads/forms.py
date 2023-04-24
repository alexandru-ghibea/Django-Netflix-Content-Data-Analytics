from django import forms
from django.core.validators import FileExtensionValidator
from .models import Csv
from django.contrib.auth import get_user_model


class CsvUploadForm(forms.Form):
    csv_file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['csv'])])

    class Meta:
        model = get_user_model()
        fields = ['csv_file']
