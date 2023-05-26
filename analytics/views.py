import base64
from django.views.generic import TemplateView
from uploads.models import Csv
import pandas as pd
from django.http import HttpResponse
import io
import matplotlib.pyplot as plt
import matplotlib
import textwrap

matplotlib.use('Agg')


class CsvAnalyticsView(TemplateView):
    template_name = 'analytics/csv_analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        filename = self.kwargs.get('filename')
        profile = self.kwargs.get('profile')
        plot_data1 = None
        plot_data = None
        plot_data2 = None
        plot_title = None
        plot_data_top_3 = None
        plot_data_top_4 = None

        if filename == 'Profiles.csv':
            selected_columns = [
                'Profile Name', 'Profile Creation Time', 'Maturity Level', 'Primary Lang']

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
            plot_data = base64.b64encode(
                buf.getvalue()).decode('utf-8')

        elif filename == 'MyList.csv':
            selected_columns = [
                "Profile Name",	"Title Name", "Utc Title Add Date"]
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
        elif filename == "ViewingActivity.csv":
            selected_columns = [
                "Profile Name", "Start Time", "Duration", "Title", "Device Type"]
            csv_file_obj = Csv.objects.filter(
                user=user, csv_file__icontains=filename).first()
            csv_file_path = csv_file_obj.csv_file.path
            df = pd.read_csv(csv_file_path, usecols=selected_columns)
            df['Duration'] = pd.to_timedelta(df['Duration'])
            df['Start Time'] = pd.to_datetime(df['Start Time'])
            df['Date'] = df['Start Time'].dt.date
            profile_names = df['Profile Name'].unique()

            # Group the data by Profile Name and calculate total duration for each profile
            duration_data = df.groupby('Profile Name')['Duration'].sum()

            # Create pie chart for total duration by profile
            fig, ax = plt.subplots()
            formatted_durations = duration_data.apply(
                lambda x: f"{x.days} days\n{x.components.hours} hrs and {x.components.minutes} minutes")
            labels = [f'{label} ({duration})' for label, duration in zip(
                duration_data.index, formatted_durations)]
            ax.pie(duration_data, autopct='%0.2f%%')

            # ax.pie(duration_data, labels=labels, autopct='%1.1f%%')

            plt.title('Duration by Profile')
            plt.legend(labels, bbox_to_anchor=(1.05, 1), loc=1)
            plt.axis('equal')
            # Save the plot to a buffer
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)

            # Add the plot to the context as an HTTP response
            plot_data = HttpResponse(buf.getvalue(), content_type='image/png')

            # Add the plot to the context as a base64-encoded string
            plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')

            # Add plots for top 3 movies/series watched/profile

            clean_df = df[selected_columns].copy()

            def extract_name(title):
                if ":" in title:
                    return title.split(":")[0]
                else:
                    return title
            clean_df.loc[:, 'Title'] = clean_df['Title'].apply(extract_name)

            # Calculate the total duration for each title across all profiles
            grouped_duration_data = clean_df.groupby(["Profile Name", "Title"]).agg({
                "Duration": "sum"}).reset_index()
            profile_totals = grouped_duration_data.groupby(
                "Profile Name").agg({"Duration": "sum"}).reset_index()
            sorted_profile_totals = profile_totals.sort_values(
                "Duration", ascending=False)
            top_3_titles = sorted_profile_totals.head(3)
            fig, axs = plt.subplots(1, 3, figsize=(
                12, 4), tight_layout=True)

            # Iterate over the top 3 titles
            for i, profile_name in enumerate(top_3_titles['Profile Name']):
                profile_data = grouped_duration_data[grouped_duration_data['Profile Name']
                                                     == profile_name].nlargest(3, 'Duration')

                # Create a bar chart for each profile
                ax = axs[i]
                ax.bar(
                    profile_data['Title'], profile_data['Duration'].dt.total_seconds() / 3600)
                ax.set_ylabel('Total View Time (hrs)')

                # Wrap the title text if it's too long

                wrapped_titles = [textwrap.fill(
                    title, 10) for title in profile_data['Title']]
                ax.set_xticklabels(wrapped_titles, wrap=True, rotation=0)
                ax.set_title(
                    f'Top 3 Titles for: \n{profile_name}', wrap=True)

                # Save the plot to a buffer
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)

                # Convert the plot to a base64-encoded string
                plot_data_top_3 = base64.b64encode(
                    buf.getvalue()).decode('utf-8')

            fig, axs = plt.subplots(3, 1, figsize=(12, 12), tight_layout=True)
            colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
            for i, profile_name in enumerate(profile_names):
                profile_data = df[df['Profile Name'] == profile_name].copy()
                profile_data.loc[:, 'Title'] = profile_data['Title'].apply(
                    extract_name)
                total_duration = profile_data.groupby('Date')['Duration'].sum()
                sorted_durations = total_duration.sort_values(ascending=False)

                top_dates = []
                top_durations = []
                top_titles = []
                for date, duration in sorted_durations.head(3).items():
                    titles = profile_data[profile_data['Date']
                                          == date]['Title'].unique()
                    title_count = len(titles)
                    top_dates.append(str(date))
                    top_durations.append(duration.total_seconds() / 3600)
                    top_titles.append('\n'.join(titles))

                ax = axs[i]
                ax.bar(top_dates, top_durations, color=colors)
                # ax.set_xlabel('Date')
                ax.set_ylabel('Total View Time (hours)')
                ax.set_title(
                    f'Top 3 Days Most Watched - \n Profile: {profile_name}')
                ax.set_xticklabels(top_dates, rotation=45)
                plt.subplots_adjust(hspace=0.5)
                plt.tight_layout()

                # Save the plot to a buffer
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)

                # Convert the plot to a base64-encoded string
                plot_data_top_4 = base64.b64encode(
                    buf.getvalue()).decode('utf-8')

        else:
            context['error_message'] = 'View not implemented yet for this file.'
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
        context['plot_data1'] = plot_data1
        context['plot_data2'] = plot_data2
        context['plot_data_top_3'] = plot_data_top_3
        context['plot_data_top_4'] = plot_data_top_4
        return context
