from uploads.models import Csv
import matplotlib.pyplot as plt
from django.views import View
from django.http import HttpResponse
import pandas as pd
import io
import matplotlib
from django.views.generic import TemplateView
matplotlib.use('Agg')

# # class PieChartView(View):
# #     def get(self, request):
# #         # Generate the data for the pie chart
# #         labels = ['Apples', 'Oranges', 'Bananas', 'Pears']
# #         sizes = [15, 30, 45, 10]

# #         # Create the pie chart
# #         fig, ax = plt.subplots()
# #         ax.pie(sizes, labels=labels, autopct='%1.1f%%')
# #         ax.set_title('Fruit Consumption')

# #         # Save the chart to a buffer
# #         buf = io.BytesIO()
# #         fig.savefig(buf, format='png')
# #         buf.seek(0)

# #         # Return the chart as an HTTP response
# #         response = HttpResponse(buf.getvalue(), content_type='image/png')
# #         return response


# # class BarChartView(View):
# #     def get(self, request):
# #         # Generate the data for the bar chart
# #         labels = ['January', 'February', 'March', 'April', 'May']
# #         values = [5, 10, 8, 12, 7]

# #         # Create the bar chart
# #         fig, ax = plt.subplots()
# #         ax.bar(labels, values)
# #         ax.set_title('Sales by Month')
# #         ax.set_xlabel('Month')
# #         ax.set_ylabel('Sales')

# #         # Save the chart to a buffer
# #         buf = io.BytesIO()
# #         fig.savefig(buf, format='png')
# #         buf.seek(0)

# #         # Return the chart as an HTTP response
# #         response = HttpResponse(buf.getvalue(), content_type='image/png')
# #         return response

# class FirstTypePivotView(View):
#     def get(self, request, *args, **kwargs):
#         user = request.user
#         csv_file_obj = Csv.objects.filter(user=user).first()
#         csv_file_path = csv_file_obj.csv_file.path
#         df = pd.read_csv(csv_file_path)
#         labels = df['Profile Name']
#         values = df['Profile Creation Time']

#         fig, ax = plt.subplots()
#         ax.bar(labels, values)
#         ax.set_title('Profiles')
#         ax.set_xlabel('Profile Name')
#         ax.set_ylabel('Profile Creation Time')
#         plt.xticks(rotation=90, ha='left')
#         buf = io.BytesIO()
#         fig.savefig(buf, format='png')
#         buf.seek(0)
#         response = HttpResponse(buf.getvalue(), content_type='image/png')
#         return response


class CsvProfileView(TemplateView):
    template_name = 'analytics/csv_profile.html'

    def get_context_data(self, **kwargs):
        context = super(CsvProfileView, self).get_context_data(**kwargs)
        user = self.request.user
        filename = self.kwargs.get('filename')
        print(filename)
        if filename == 'Profiles.csv':
            selected_columns = ['Profile Name',
                                'Profile Creation Time', 'Maturity Level', "Primary Lang"]
        elif filename == 'AccountDetails.csv':
            selected_columns = ['Profile Name',
                                'Profile Creation Time', 'Primary Lang']
        # else:
        #     selected_columns = [
        #         'Profile Name', 'Profile Creation Time', 'Maturity Level', 'Primary Lang']

        csv_file_obj = Csv.objects.filter(
            user=user, csv_file__icontains=filename).first()
        csv_file_path = csv_file_obj.csv_file.path

        df = pd.read_csv(csv_file_path, usecols=selected_columns)
        table_data = df.to_dict('records')
        print(table_data)
        context['table_data'] = table_data

        return context
