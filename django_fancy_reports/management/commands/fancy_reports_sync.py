# django_fancy_reports/management/commands/sync_reports.py
from django.core.management.base import BaseCommand
from django_fancy_reports.registry import registry
from django_fancy_reports.models import Report, ReportTheme, ReportPageFormat


class Command(BaseCommand):
    help = 'Sync registered reports to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing report configurations',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created/updated without making changes',
        )

    def handle(self, *args, **options):
        registered_reports = registry.all()
        overwrite = options['overwrite']
        dry_run = options['dry_run']

        if not registered_reports:
            self.stdout.write(
                self.style.WARNING('No reports registered. Make sure your reports.py files are being imported.')
            )
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0

        self.stdout.write(f"\n{'=' * 80}")
        self.stdout.write(f"Found {len(registered_reports)} registered report(s)")
        self.stdout.write(f"{'=' * 80}\n")

        for name, report_class in registered_reports.items():
            # Check if report exists
            try:
                report_obj = Report.objects.get(report_name=name)
                exists = True
            except Report.DoesNotExist:
                report_obj = None
                exists = False

            # Resolve theme if specified
            theme = None
            if report_class.default_theme:
                theme = ReportTheme.objects.filter(
                    name=report_class.default_theme,
                    is_active=True
                ).first()
                if not theme:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠ Theme '{report_class.default_theme}' not found for {name}"
                        )
                    )

            # Resolve page format if specified
            page_format = None
            if report_class.default_page_format:
                page_format = ReportPageFormat.objects.filter(
                    name=report_class.default_page_format
                ).first()
                if not page_format:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠ Page format '{report_class.default_page_format}' not found for {name}"
                        )
                    )

            if exists and not overwrite:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f"  • {name}")
                )
                self.stdout.write(
                    f"    Status: Already exists (use --overwrite to update)"
                )
            elif exists and overwrite:
                # Update existing
                if not dry_run:
                    report_obj.display_name = report_class.display_name or name
                    report_obj.description = report_class.description
                    report_obj.text_direction = report_class.text_direction
                    report_obj.custom_css = report_class.custom_css
                    if theme:
                        report_obj.theme = theme
                    if page_format:
                        report_obj.page_format = page_format
                    report_obj.save()

                updated_count += 1
                status = "(would update)" if dry_run else "✓ Updated"
                self.stdout.write(
                    self.style.SUCCESS(f"  • {name}")
                )
                self.stdout.write(f"    Status: {status}")
                self._print_details(report_class, theme, page_format)
            else:
                # Create new
                if not dry_run:
                    Report.objects.create(
                        report_name=name,
                        display_name=report_class.display_name or name,
                        description=report_class.description,
                        theme=theme,
                        page_format=page_format,
                        text_direction=report_class.text_direction,
                        custom_css=report_class.custom_css,
                    )

                created_count += 1
                status = "(would create)" if dry_run else "✓ Created"
                self.stdout.write(
                    self.style.SUCCESS(f"  • {name}")
                )
                self.stdout.write(f"    Status: {status}")
                self._print_details(report_class, theme, page_format)

        # Summary
        self.stdout.write(f"\n{'=' * 80}")
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Created: {created_count}")
            )
        if updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Updated: {updated_count}")
            )
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(f"⊘ Skipped: {skipped_count}")
            )
        if dry_run:
            self.stdout.write(
                self.style.NOTICE("\n(Dry run - no changes made)")
            )
        self.stdout.write(f"{'=' * 80}\n")

    def _print_details(self, report_class, theme, page_format):
        """Print report configuration details"""
        self.stdout.write(f"    Display Name: {report_class.display_name or 'N/A'}")
        self.stdout.write(f"    Text Direction: {report_class.text_direction}")
        if theme:
            self.stdout.write(f"    Theme: {theme.name}")
        if page_format:
            self.stdout.write(f"    Page Format: {page_format.name}")
        if report_class.description:
            self.stdout.write(f"    Description: {report_class.description}")
        self.stdout.write("")  # Empty line for spacing
