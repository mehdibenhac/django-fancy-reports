from django.core.management.base import BaseCommand, CommandError
from django_fancy_reports.registry import registry
from django_fancy_reports.urls import get_reports_url_prefix


class Command(BaseCommand):
    help = 'Show detailed information about a specific report'

    def add_arguments(self, parser):
        parser.add_argument(
            'report_name',
            type=str,
            help='Full report name (e.g., "invoices.InvoiceReport")',
        )

    def handle(self, *args, **options):
        from django_fancy_reports.models import Report

        report_name = options['report_name']

        # Get report class from registry
        report_class = registry.get(report_name)
        if not report_class:
            raise CommandError(
                f'Error: Report "{report_name}" not found. '
                f'Use "python manage.py list_reports" to see available reports.'
            )

        # Get report configuration from database
        try:
            config = Report.objects.get(report_name=report_name)
            has_config = True
        except Report.DoesNotExist:
            config = None
            has_config = False

        # Display report information
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.HTTP_INFO(f'Report: {report_name}'))
        self.stdout.write('=' * 80 + '\n')

        # Basic information
        self.stdout.write(self.style.HTTP_INFO('BASIC INFORMATION:'))
        self.stdout.write(f'  Report Name: {report_name}')
        display_name = report_class.display_name or report_name
        self.stdout.write(f'  Display Name: {display_name}')

        if report_class.description:
            self.stdout.write(f'  Description: {report_class.description}')

        self.stdout.write(f'  Template: {report_class.template_name or "Not specified"}')

        # Configuration status
        self.stdout.write(f'\n{self.style.HTTP_INFO("CONFIGURATION:")}')
        if has_config:
            self.stdout.write(self.style.SUCCESS('  ✓ Configured in database'))

            # Theme
            if config.theme:
                self.stdout.write(f'  Theme: {config.theme.name} (ID: {config.theme.id})')
            else:
                self.stdout.write('  Theme: Using default')

            # Page format
            if config.page_format:
                self.stdout.write(
                    f'  Page Format: {config.page_format.name} (ID: {config.page_format.id})'
                )
            else:
                self.stdout.write('  Page Format: Using default')

            # Text direction
            self.stdout.write(f'  Text Direction: {config.text_direction.upper()}')

            # Custom CSS
            if config.custom_css:
                lines = len(config.custom_css.splitlines())
                self.stdout.write(f'  Custom CSS: Yes ({lines} lines)')
            else:
                self.stdout.write('  Custom CSS: No')
        else:
            self.stdout.write(self.style.WARNING('  ✗ Not configured in database'))
            self.stdout.write('  Using class defaults and global settings')

        # Class defaults
        self.stdout.write(f'\n{self.style.HTTP_INFO("CLASS DEFAULTS:")}')
        self.stdout.write(f'  Text Direction: {report_class.text_direction}')
        formats = ', '.join(report_class.allowed_formats)
        self.stdout.write(f'  Allowed Formats: {formats}')

        # Example commands
        self.stdout.write(f'\n{self.style.HTTP_INFO("EXAMPLE COMMANDS:")}')

        # HTML generation
        self.stdout.write(f'  Generate HTML:')
        self.stdout.write(f'    python manage.py print_report {report_name} --format html')

        # PDF generation
        self.stdout.write(f'  Generate PDF:')
        self.stdout.write(
            f'    python manage.py print_report {report_name} --format pdf -o output.pdf'
        )

        # With record ID
        self.stdout.write(f'  With record ID:')
        self.stdout.write(
            f'    python manage.py print_report {report_name} --record-id 123 --format pdf'
        )

        # With custom theme/format
        if has_config:
            if config.theme:
                self.stdout.write(f'  With custom theme:')
                self.stdout.write(
                    f'    python manage.py print_report {report_name} '
                    f'--theme {config.theme.id} --format html'
                )

        self.stdout.write('\n' + '=' * 80 + '\n')
