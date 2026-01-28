from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Load default fixtures for Django Fancy Reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-formats',
            action='store_true',
            help='Skip loading page formats',
        )
        parser.add_argument(
            '--skip-themes',
            action='store_true',
            help='Skip loading themes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force loading even if data already exists',
        )

    def handle(self, *args, **options):
        from django_fancy_reports.models import ReportPageFormat, ReportTheme

        # Check if data already exists
        formats_exist = ReportPageFormat.objects.exists()
        themes_exist = ReportTheme.objects.exists()

        if not options['force']:
            if formats_exist and not options['skip_formats']:
                self.stdout.write(
                    self.style.WARNING(
                        'Page formats already exist. Use --force to load anyway.'
                    )
                )
                options['skip_formats'] = True

            if themes_exist and not options['skip_themes']:
                self.stdout.write(
                    self.style.WARNING(
                        'Themes already exist. Use --force to load anyway.'
                    )
                )
                options['skip_themes'] = True

        # Load fixtures
        if not options['skip_formats']:
            self.stdout.write('Loading page formats...')
            call_command('loaddata', 'page_formats', verbosity=0)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Loaded {ReportPageFormat.objects.count()} page format(s)'
                )
            )

        if not options['skip_themes']:
            self.stdout.write('Loading themes...')
            call_command('loaddata', 'themes', verbosity=0)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Loaded {ReportTheme.objects.count()} theme(s)'
                )
            )

        self.stdout.write(
            self.style.SUCCESS('\n✓ Fixtures loaded successfully!')
        )
