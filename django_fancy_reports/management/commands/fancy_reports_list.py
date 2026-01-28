from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'List all registered reports (alias for print_report --list)'

    def handle(self, *args, **options):
        # Simply delegate to fancy_reports_print --list
        call_command('fancy_reports_print', list=True)
