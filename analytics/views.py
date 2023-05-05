from uploads.models import Csv
import pandas as pd
from django.views.generic import TemplateView


class CsvProfileView(TemplateView):
    template_name = 'analytics/csv_profile.html'

    def get_context_data(self, **kwargs):
        context = super(CsvProfileView, self).get_context_data(**kwargs)
        user = self.request.user
        filename = self.kwargs.get('filename')
        if filename == 'Profiles.csv':
            selected_columns = ['Profile Name',
                                'Profile Creation Time', 'Maturity Level', "Primary Lang"]
            chart_data = None
        else:
            context['error_message'] = 'Not implemented yet'
            return context
        csv_file_obj = Csv.objects.filter(
            user=user, csv_file__icontains=filename).first()
        csv_file_path = csv_file_obj.csv_file.path

        df = pd.read_csv(csv_file_path, usecols=selected_columns)
        table_data = df.to_dict('records')
        context['table_data'] = table_data
        return context
