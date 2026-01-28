import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render
from django.views import View

from .registry import registry
from .base import ReportFormat
from .models import Report

if TYPE_CHECKING:
    from django.http import HttpRequest

logger = logging.getLogger(__name__)


class ReportListView(View):
    """View to list all available reports"""

    def get(self, request):
        # Get all registered reports
        registered_reports = registry.all()

        # Get URL prefix from settings
        url_prefix = getattr(settings, 'REPORTS_URL_PREFIX', 'reports')

        # Get report configurations from database
        report_configs = {
            r.report_name: r
            for r in Report.objects.all()
        }

        # Combine information
        reports_info = []
        for name, report_class in registered_reports.items():
            config = report_configs.get(name)

            reports_info.append({
                'name': name,
                'display_name': report_class.display_name or name,
                'description': report_class.description,
                'is_configured': config is not None,
                'url_prefix': url_prefix,
            })

        # Sort by display name
        reports_info.sort(key=lambda x: x['display_name'])

        context = {
            'reports': reports_info,
        }

        return render(request, 'django_fancy_reports/report_list.html', context)


class ReportView(View):
    """Generic view for rendering reports"""

    def get(
            self,
            request: 'HttpRequest',
            output_format: str,
            report_name: str,
            record_id: str | None = None
    ) -> HttpResponse:
        """
        Render a report in the specified format.

        URL parameters:
            - output_format: html, pdf, or text
            - report_name: Full report name (e.g., 'invoices.InvoiceReport')
            - record_id: Optional ID of the record

        Query parameters:
            - theme_id: ID of ReportTheme to use
            - page_format_id: ID of ReportPageFormat to use
            - text_direction: 'ltr' or 'rtl'
        """
        # Validate format
        output_format = output_format.lower()
        if output_format not in ReportFormat.get_all():
            return HttpResponseBadRequest(
                f"Invalid format: {output_format}. "
                f"Allowed formats: {', '.join(ReportFormat.get_all())}"
            )

        # Get report class from registry
        report_class = registry.get(report_name)
        if not report_class:
            raise Http404(f"Report not found: {report_name}")

        # Get query parameters
        theme_id = request.GET.get('theme_id')
        page_format_id = request.GET.get('page_format_id')
        text_direction = request.GET.get('text_direction')

        # Convert IDs to integers if provided
        theme = int(theme_id) if theme_id else None
        page_format = int(page_format_id) if page_format_id else None

        # Instantiate report
        try:
            report = report_class(
                record_id=record_id,
                text_direction=text_direction,
                theme_instance=theme,
                page_format_instance=page_format
            )
        except Exception as e:
            logger.error(f"Error instantiating report {report_name}: {e}", exc_info=True)
            return HttpResponseBadRequest(f"Error creating report: {str(e)}")

        # Render report
        try:
            content = report.render(output_format=output_format)
        except Exception as e:
            logger.error(f"Error rendering report {report_name}: {e}", exc_info=True)
            return HttpResponseBadRequest(f"Error rendering report: {str(e)}")

        # Prepare response based on format
        if output_format == ReportFormat.HTML:
            response = HttpResponse(content, content_type='text/html; charset=utf-8')
        elif output_format == ReportFormat.PDF:
            response = HttpResponse(content, content_type='application/pdf')
            filename = report.get_filename(output_format=output_format)
            response['Content-Disposition'] = f'inline; filename="{filename}"'
        elif output_format == ReportFormat.TEXT:
            response = HttpResponse(content, content_type='text/plain; charset=utf-8')
            filename = report.get_filename(output_format=output_format)
            response['Content-Disposition'] = f'inline; filename="{filename}"'
        else:
            return HttpResponseBadRequest(f"Unknown format: {output_format}")

        return response
