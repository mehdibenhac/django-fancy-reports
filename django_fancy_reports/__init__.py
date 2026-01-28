"""
Django Fancy Reports - A customizable and extensible reporting framework for Django
"""

__version__ = "0.1.0"

default_app_config = 'django_fancy_reports.apps.DjangoFancyReportsConfig'

from .base import BaseReport, ReportFormat
from .registry import registry

__all__ = ['BaseReport', 'ReportFormat', 'registry']
