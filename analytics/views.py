import requests
import base64
from django.views.generic import TemplateView
from uploads.models import Csv
import pandas as pd
from django.http import HttpResponse
import io
import matplotlib.pyplot as plt
import matplotlib
import textwrap
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist

matplotlib.use('Agg')

# For the plot titles


def extract_name(title):
    if ":" in title:
        return title.split(":")[0]
    else:
        return title


class CsvAnalyticsView(TemplateView):
    def get_template_names(self):
        filename = self.kwargs.get('filename')
        template_name = f'analytics/{filename.lower().replace(".csv", "")}_analytics.html'

        try:
            get_template(template_name)
        except TemplateDoesNotExist:
            template_name = 'analytics/analytics_not_available.html'
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        filename = self.kwargs.get('filename')

        if filename == 'Profiles.csv':
            return ProfilesAnalytics().get_context_data(context, user)

        elif filename == 'BillingHistory.csv':
            return BillingHistoryAnalytics().get_context_data(context, user)

        elif filename == 'MyList.csv':
            return MyListAnalytics().get_context_data(context, user, self.kwargs.get('profile'))

        elif filename == 'ViewingActivity.csv':
            context = ProfilesTotalWatchTimeAnalytics().get_context_data(context, user)
            context = Top3MostWatchedAnalytics().get_context_data(context, user)
            context = Top3DaysAnalytics().get_context_data(context, user)
            context = TopDaysAnalytics().get_context_data(context, user)
            context = TopHoursAnalytics().get_context_data(context, user)
            return context
        # if the file is not one of the above, return an error message
        else:
            context['error_message'] = 'Analytics not available yet for this file. Contact us for more information.'
            return context


class ProfilesAnalytics:
    @staticmethod
    def get_context_data(context, user):
        selected_columns = [
            'Profile Name', 'Profile Creation Time', 'Maturity Level', 'Primary Lang']

        # Get the table data
        csv_file_obj = Csv.objects.filter(
            user=user, csv_file__icontains='Profiles.csv').first()
        csv_file_path = csv_file_obj.csv_file.path
        df = pd.read_csv(csv_file_path, usecols=selected_columns)
        table_data = df.to_dict('records')

        # Add the data to the context
        context['table_data'] = table_data
        return context


class BillingHistoryAnalytics:
    @staticmethod
    def get_context_data(context, user):
        selected_columns = ['Transaction Date', 'Payment Type',
                            'Country', 'Currency', 'Gross Sale Amt', 'Pmt Status']
        plot_title = 'Gross Sale Amount by Currency and Payment Status'

        # Get the data from the CSV file
        csv_file_obj = Csv.objects.filter(
            user=user, csv_file__icontains='BillingHistory.csv').first()
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
        ax = grouped_data.plot(
            x="Pmt Status", y="Gross Sale Amt", kind='bar', rot=0, ax=ax)

        # Display the values on top of the bars
        # for i, row in grouped_data.iterrows():
        #     ax.text(i, row["Gross Sale Amt"], str(
        #         row["Gross Sale Amt"]), ha="center")

        plt.title(plot_title)
        plt.xlabel("Payment Status")
        plt.ylabel("Currency (in EUR)")

        # Save the plot to a buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)

        # Add the plot to the context as an HTTP response
        plot_data_billing = HttpResponse(
            buf.getvalue(), content_type='image/png')

        # Add the plot to the context as a base64-encoded string
        plot_data_billing = base64.b64encode(buf.getvalue()).decode('utf-8')

        # Add the data to the context
        context['plot_data_billing'] = plot_data_billing
        return context


class MyListAnalytics:
    @staticmethod
    def get_context_data(context, user, profile):
        selected_columns = ["Profile Name", "Title Name", "Utc Title Add Date"]

        # Get the table data
        csv_file_obj = Csv.objects.filter(
            user=user, csv_file__icontains='MyList.csv').first()
        csv_file_path = csv_file_obj.csv_file.path
        df = pd.read_csv(csv_file_path, usecols=selected_columns)
        clean_df = df.dropna().drop_duplicates()
        table_data = clean_df.to_dict('records')
        context['table_data'] = table_data
        return context


class ProfilesTotalWatchTimeAnalytics:
    @staticmethod
    def get_context_data(context, user):
        selected_columns = ["Profile Name", "Start Time",
                            "Duration", "Title", "Device Type"]

        # Get the table data
        csv_file_obj = Csv.objects.filter(
            user=user, csv_file__icontains='ViewingActivity.csv').first()
        csv_file_path = csv_file_obj.csv_file.path
        df = pd.read_csv(csv_file_path, usecols=selected_columns)
        df['Duration'] = pd.to_timedelta(df['Duration'])
        df['Start Time'] = pd.to_datetime(df['Start Time'])
        df['Date'] = df['Start Time'].dt.date

        # Group the data by Profile Name and calculate total duration for each profile
        duration_data = df.groupby('Profile Name')['Duration'].sum()

        # Create pie chart for total duration by profile
        fig, ax = plt.subplots(figsize=(4, 4))
        formatted_durations = duration_data.apply(
            lambda x: f"{x.days} days\n{x.components.hours} hrs and {x.components.minutes} minutes")
        labels = [f'{label} ({duration})' for label, duration in zip(
            duration_data.index, formatted_durations)]
        ax.pie(duration_data, autopct='%0.2f%%')

        plt.title('View Time by Profile')
        plt.legend(labels, bbox_to_anchor=(1.05, 1), loc=1)
        plt.axis('equal')

        # Save the plot to a buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)

        # Add the plot to the context as an HTTP response
        plot_data_watch_time = HttpResponse(
            buf.getvalue(), content_type='image/png')

        # Add the plot to the context as a base64-encoded string
        plot_data_watch_time = base64.b64encode(buf.getvalue()).decode('utf-8')

        # Add the data to the context
        context['plot_data_watch_time'] = plot_data_watch_time

        return context


class Top3MostWatchedAnalytics:
    @staticmethod
    def get_context_data(context, user):
        selected_columns = ["Profile Name", "Start Time",
                            "Duration", "Title", "Device Type"]

        # Get the table data
        csv_file_obj = Csv.objects.filter(
            user=user, csv_file__icontains='ViewingActivity.csv').first()
        csv_file_path = csv_file_obj.csv_file.path
        df = pd.read_csv(csv_file_path, usecols=selected_columns)
        df['Duration'] = pd.to_timedelta(df['Duration'])
        df['Start Time'] = pd.to_datetime(df['Start Time'])
        df['Date'] = df['Start Time'].dt.date

        # Group the data by Profile Name and calculate total duration for each profile
        clean_df = df[selected_columns].copy()
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

            # Convert the plot to an HTTP response
            plot_data_top_3_most_watched = HttpResponse(
                buf.getvalue(), content_type='image/png')

            # Convert the plot to a base64-encoded string
            plot_data_top_3_most_watched = base64.b64encode(
                buf.getvalue()).decode('utf-8')
            context['plot_data_top_3_most_watched'] = plot_data_top_3_most_watched
        return context


class Top3DaysAnalytics:
    @staticmethod
    def get_context_data(context, user):
        selected_columns = ["Profile Name", "Start Time",
                            "Duration", "Title", "Device Type"]
        # Get the table data
        csv_file_obj = Csv.objects.filter(
            user=user, csv_file__icontains='ViewingActivity.csv').first()
        csv_file_path = csv_file_obj.csv_file.path
        df = pd.read_csv(csv_file_path, usecols=selected_columns)
        df['Duration'] = pd.to_timedelta(df['Duration'])
        df['Start Time'] = pd.to_datetime(df['Start Time'])
        df['Date'] = df['Start Time'].dt.date
        profile_names = df['Profile Name'].unique()
        fig, axs = plt.subplots(1, 3, figsize=(12, 4), tight_layout=True)
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
                top_dates.append(str(date))
                top_durations.append(duration.total_seconds() / 3600)
                top_titles.append('\n'.join(titles))

            ax = axs[i]
            ax.bar(top_dates, top_durations, color=colors)
            # ax.set_xlabel('Date')
            ax.set_ylabel('Total View Time (hours)')
            ax.set_title(
                f'Top 3 Days Most Watched \n Profile: {profile_name}')
            ax.set_xticklabels(top_dates, rotation=45)
            plt.subplots_adjust(hspace=0.5)
            plt.tight_layout()

            # Save the plot to a buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)

            # Add the plot to the context as an HTTP response
            plot_data_top_3_days_most_watched = HttpResponse(
                buf.getvalue(), content_type='image/png')

            # Add the plot to the context as a base64-encoded string
            plot_data_top_3_days_most_watched = base64.b64encode(
                buf.getvalue()).decode('utf-8')
            context['plot_data_top_3_days_most_watched'] = plot_data_top_3_days_most_watched
        return context

# View for most watched days/months for each user


class TopDaysAnalytics:
    @staticmethod
    def get_context_data(context, user):
        selected_columns = ["Profile Name", "Start Time",
                            "Duration", "Title", "Device Type"]
        # Get the table data
        csv_file_obj = Csv.objects.filter(
            user=user, csv_file__icontains='ViewingActivity.csv').first()
        csv_file_path = csv_file_obj.csv_file.path
        df = pd.read_csv(csv_file_path, usecols=selected_columns)
        df['Duration'] = pd.to_timedelta(df['Duration'])
        df['Start Time'] = pd.to_datetime(df['Start Time'])
        df['Day of Week'] = df['Start Time'].dt.day_name()
        profile_names = df['Profile Name'].unique()
        fig, axs = plt.subplots(1, 3, figsize=(12, 4), tight_layout=True)
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        for i, profile_name in enumerate(profile_names):
            profile_data = df[df['Profile Name'] == profile_name].copy()
            profile_data.loc[:, 'Title'] = profile_data['Title'].apply(
                extract_name)
            total_duration = profile_data.groupby(
                'Day of Week')['Duration'].sum()
            sorted_durations = total_duration.sort_values(ascending=False)

            top_dates = []
            top_durations = []
            top_titles = []
            for day, duration in sorted_durations.items():
                titles = profile_data[profile_data['Day of Week']
                                      == day]['Title'].unique()
                top_dates.append(day)
                top_durations.append(duration.total_seconds() / 3600)
                top_titles.append('\n'.join(titles))

            ax = axs[i]
            ax.bar(top_dates, top_durations, color=colors)
            ax.set_ylabel('Total View Time (hours)')
            ax.set_title(
                f'Most Watched Days of the Week \n Profile: {profile_name}')
            ax.set_xticklabels(top_dates, rotation=45)
            plt.subplots_adjust(hspace=0.5)
            plt.tight_layout()

            # Save the plot to a buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)

            # Add the plot to the context as an HTTP response
            plot_data_most_watched_days = HttpResponse(
                buf.getvalue(), content_type='image/png')

            # Add the plot to the context as a base64-encoded string
            plot_data_most_watched_days = base64.b64encode(
                buf.getvalue()).decode('utf-8')
            context['plot_data_most_watched_days'] = plot_data_most_watched_days
            # calculated_duration = df.groupby(['Profile Name', 'Day of Week'])[
            #     'Duration'].sum()
            # print(calculated_duration)
        return context


class TopHoursAnalytics:
    @staticmethod
    def get_context_data(context, user):
        selected_columns = ["Profile Name", "Start Time",
                            "Duration", "Title", "Device Type"]
        # Get the table data
        csv_file_obj = Csv.objects.filter(
            user=user, csv_file__icontains='ViewingActivity.csv').first()
        csv_file_path = csv_file_obj.csv_file.path
        df = pd.read_csv(csv_file_path, usecols=selected_columns)
        df['Duration'] = pd.to_timedelta(df['Duration'])
        df['Start Time'] = pd.to_datetime(df['Start Time'])
        df['Hour Interval'] = pd.cut(df['Start Time'].dt.hour, bins=[
                                     0, 7, 15, 23], labels=['Night', 'Morning', 'Evening'])
        profile_names = df['Profile Name'].unique()
        fig, axs = plt.subplots(1, 3, figsize=(12, 4), tight_layout=True)
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        for i, profile_name in enumerate(profile_names):
            profile_data = df[df['Profile Name'] == profile_name].copy()
            profile_data.loc[:, 'Title'] = profile_data['Title'].apply(
                extract_name)
            total_duration = profile_data.groupby(
                'Hour Interval')['Duration'].sum().dt.total_seconds() / 3600
            sorted_durations = total_duration.sort_values(ascending=False)

            top_intervals = []
            top_durations = []
            top_titles = []
            for interval, duration in sorted_durations.items():
                titles = profile_data[profile_data['Hour Interval']
                                      == interval]['Title'].unique()
                top_intervals.append(interval)
                top_durations.append(duration)
                top_titles.append('\n'.join(titles))

            ax = axs[i]
            ax.bar(top_intervals, top_durations, color=colors)
            ax.set_ylabel('Total View Time (hours)')
            ax.set_title(
                f"Most Watched Hours of the Day \n Profile: {profile_name}")
            ax.set_xticklabels(top_intervals, rotation=45)
            plt.subplots_adjust(hspace=0.5)
            plt.tight_layout()

            # Save the plot to a buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)

            # Add the plot to the context as an HTTP response
            plot_data_most_watched_hours = HttpResponse(
                buf.getvalue(), content_type='image/png')

            # Add the plot to the context as a base64-encoded string
            plot_data_most_watched_hours = base64.b64encode(
                buf.getvalue()).decode('utf-8')
            context['plot_data_most_watched_hours'] = plot_data_most_watched_hours
        return context
