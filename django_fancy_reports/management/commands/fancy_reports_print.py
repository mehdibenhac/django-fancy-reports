import sys

from django.core.management.base import BaseCommand, CommandError
from django_fancy_reports.registry import registry
from django_fancy_reports.base import ReportFormat


class Command(BaseCommand):
    help = 'Generate and output a report from the command line'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            'report_name',
            type=str,
            nargs='?',
            help='Full report name (e.g., "invoices.InvoiceReport")',
        )

        # Report generation options
        parser.add_argument(
            '--format',
            type=str,
            choices=ReportFormat.get_all(),
            default=ReportFormat.HTML,
            help='Output format (html, pdf, text). Default: html',
        )
        parser.add_argument(
            '--record-id',
            type=str,
            help='Record ID to generate report for',
        )
        parser.add_argument(
            '--text-direction',
            type=str,
            choices=['ltr', 'rtl'],
            default='ltr',
            help='Text direction (ltr or rtl). Default: ltr',
        )
        parser.add_argument(
            '--theme',
            type=int,
            help='Theme ID to use',
        )
        parser.add_argument(
            '--page-format',
            type=int,
            help='Page format ID to use',
        )

        # Output options
        parser.add_argument(
            '--output',
            '-o',
            type=str,
            help='Output file path. If not specified, outputs to stdout',
        )

        # List reports
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all registered reports and exit',
        )

        # Verbose mode
        parser.add_argument(
            '--quiet',
            '-q',
            action='store_true',
            help='Suppress informational messages',
        )

    def handle(self, *args, **options):
        # Handle --list option
        if options['list']:
            self.list_reports()
            return

        # Validate report_name is provided
        report_name = options['report_name']
        if not report_name:
            raise CommandError(
                'Error: report_name is required. Use --list to see available reports.'
            )

        # Get report class from registry
        report_class = registry.get(report_name)
        if not report_class:
            raise CommandError(
                f'Error: Report "{report_name}" not found. '
                f'Use --list to see available reports.'
            )

        # Extract options
        record_id = options['record_id']
        format_type = options['format']
        text_direction = options['text_direction']
        theme_id = options['theme']
        page_format_id = options['page_format']
        output_path = options['output']
        quiet = options['quiet']

        # Log report generation
        if not quiet:
            self.stdout.write(f'Generating report: {report_name}')
            if record_id:
                self.stdout.write(f'  Record ID: {record_id}')
            self.stdout.write(f'  Format: {format_type}')
            self.stdout.write(f'  Text direction: {text_direction}')
            if theme_id:
                self.stdout.write(f'  Theme ID: {theme_id}')
            if page_format_id:
                self.stdout.write(f'  Page format ID: {page_format_id}')

        # Instantiate report
        try:
            report = report_class(
                record_id=record_id,
                text_direction=text_direction,
                theme=theme_id,
                page_format=page_format_id,
            )
        except Exception as e:
            raise CommandError(f'Error instantiating report: {e}')

        # Render report
        try:
            content = report.render(format=format_type)
        except Exception as e:
            raise CommandError(f'Error rendering report: {e}')

        # Output to file or stdout
        if output_path:
            # Write to file
            mode = 'wb' if format_type == ReportFormat.PDF else 'w'
            encoding = None if format_type == ReportFormat.PDF else 'utf-8'

            try:
                with open(output_path, mode, encoding=encoding) as f:
                    f.write(content)

                if not quiet:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Report saved to: {output_path}')
                    )
            except Exception as e:
                raise CommandError(f'Error writing to file: {e}')
        else:
            # Write to stdout
            if format_type == ReportFormat.PDF:
                # For PDF, write binary to stdout
                sys.stdout.buffer.write(content)
            else:
                # For HTML/Text, write as string
                self.stdout.write(content)

    def list_reports(self):
        """List all registered reports"""
        from django_fancy_reports.models import Report

        all_reports = registry.all()

        if not all_reports:
            self.stdout.write(
                self.style.WARNING('No reports registered.')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'\nRegistered Reports ({len(all_reports)}):')
        )
        self.stdout.write('=' * 80)

        # Get report configurations from database
        report_configs = {
            r.report_name: r
            for r in Report.objects.all()
        }

        for name, report_class in sorted(all_reports.items()):
            config = report_configs.get(name)

            self.stdout.write(f'\n{self.style.HTTP_INFO(name)}')

            # Display name
            display_name = report_class.display_name or name
            self.stdout.write(f'  Display Name: {display_name}')

            # Description
            if report_class.description:
                self.stdout.write(f'  Description: {report_class.description}')

            # Status
            if config:
                # Text direction
                self.stdout.write(f'  Text Direction: {config.text_direction.upper()}')
            else:
                self.stdout.write(
                    f'  Status: {self.style.WARNING("Not configured in database")}'
                )

            # Example usage
            self.stdout.write(
                f'  Example: python manage.py fancy_reports_print {name} --format html'
            )

        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(
            f'\nUse: python manage.py fancy_reports_print <report_name> --format <format>\n'
        )
