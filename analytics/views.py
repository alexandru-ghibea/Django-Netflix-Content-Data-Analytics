import base64
from django.views.generic import TemplateView
from uploads.models import Csv
import pandas as pd
from django.views.generic import TemplateView
import numpy as np
from django.http import HttpResponse
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


class CsvAnalyticsView(TemplateView):
    template_name = 'analytics/csv_analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        filename = self.kwargs.get('filename')
        profile = self.kwargs.get('profile')
        paginate_by = 5

        if filename == 'Profiles.csv':
            selected_columns = [
                'Profile Name', 'Profile Creation Time', 'Maturity Level', 'Primary Lang']
            plot_title = None
            plot_data = None
        elif filename == 'BillingHistory.csv':
            selected_columns = ['Transaction Date', 'Payment Type',
                                'Country', 'Currency', 'Gross Sale Amt', 'Pmt Status']
            plot_title = 'Gross Sale Amount by Currency and Payment Status'

            # Get the data from the CSV file
            csv_file_obj = Csv.objects.filter(
                user=user, csv_file__icontains=filename).first()
            csv_file_path = csv_file_obj.csv_file.path
            df = pd.read_csv(csv_file_path, usecols=selected_columns)

            # remove NaN values and duplicates
            clean_df = df.dropna().drop_duplicates()

            # remove rows where Pmt Status is "New"
            filtered_df = clean_df.drop(
                clean_df.index[clean_df['Pmt Status'].isin(["NEW", "PENDING", "CANCELED"])])

            # Group the data by Payment Status and Currency
            grouped_data = filtered_df.groupby(["Pmt Status", "Currency"])[
                "Gross Sale Amt"].sum().reset_index()

            # Plot the bar chart
            fig, ax = plt.subplots()
            ax = grouped_data.plot(x="Pmt Status", y="Gross Sale Amt",
                                   kind='bar', rot=0, ax=ax)

            for i, row in grouped_data.iterrows():
                ax.text(i, row["Gross Sale Amt"], str(
                    row["Gross Sale Amt"]), ha="center")
            plt.title("Gross Sale Amount by Currency and Payment Status")
            plt.xlabel("Payment Status")
            plt.ylabel("EUR")

            # Save the plot to a buffer
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)

            # Add the plot to the context as an HTTP response
            plot_data = HttpResponse(buf.getvalue(), content_type='image/png')

            # Add the plot to the context as a base64-encoded string
            plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')

        elif filename == 'MyList.csv':
            selected_columns = [
                "Profile Name",	"Title Name", "Utc Title Add Date"]
            plot_data = None
            plot_title = None
            csv_file_obj = Csv.objects.filter(
                user=user, csv_file__icontains=filename).first()
            csv_file_path = csv_file_obj.csv_file.path
            df = pd.read_csv(csv_file_path, usecols=selected_columns)
            filtered_df = df[df["Profile Name"] == profile]
            pivot_df = pd.pivot_table(filtered_df, index=["Profile Name"], columns=[
                                      "Title Name"], values=["Utc Title Add Date"], aggfunc=len, fill_value=0)
            pivot_dict = pivot_df.to_dict('index')
            context = {
                'profiles': df["Profile Name"].unique(),
                'titles': df["Title Name"],
                'pivot_dict': pivot_dict,
                'selected_profile': profile,
            }
        else:
            context['error_message'] = 'Not implemented yet'
            context['plot_message'] = 'Plot not available for this file yet.'
            return context

        # Get the table data
        csv_file_obj = Csv.objects.filter(
            user=user, csv_file__icontains=filename).first()
        csv_file_path = csv_file_obj.csv_file.path
        df = pd.read_csv(csv_file_path, usecols=selected_columns)
        table_data = df.to_dict('records')

        # Add the data to the context
        context['table_data'] = table_data
        context['plot_title'] = plot_title
        context['plot_data'] = plot_data
        return context
