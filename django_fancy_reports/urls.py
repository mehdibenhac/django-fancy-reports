from django.urls import path
from django.conf import settings
from .views import ReportView, ReportListView

app_name = 'django_fancy_reports'

# Get the configured prefix
prefix = getattr(settings, 'REPORTS_URL_PREFIX', 'reports')

urlpatterns = [
    # List all reports
    path(f'{prefix}/', ReportListView.as_view(), name='report_list'),

    # Report without record ID
    path(
        f'{prefix}/<str:output_format>/<str:report_name>/',
        ReportView.as_view(),
        name='report'
    ),

    # Report with record ID
    path(
        f'{prefix}/<str:output_format>/<str:report_name>/<str:record_id>/',
        ReportView.as_view(),
        name='report_with_id'
    ),
]
