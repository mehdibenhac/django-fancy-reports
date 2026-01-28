import logging
from typing import Type, Dict
from django.apps import apps
from django.utils.module_loading import import_module

logger = logging.getLogger(__name__)


class ReportRegistry:
    """Registry for all report classes"""

    def __init__(self):
        self._reports: Dict[str, Type['BaseReport']] = {}

    def register(self, report_class: Type['BaseReport']) -> Type['BaseReport']:
        """
        Register a report class.

        Args:
            report_class: The report class to register

        Returns:
            The report class (for chaining)

        Raises:
            ValueError: If report_name is not defined or already registered
        """
        if not report_class.report_name:
            raise ValueError(
                f"{report_class.__name__} must define a 'report_name' attribute"
            )

        if report_class.report_name in self._reports:
            logger.warning(
                f"Report '{report_class.report_name}' is already registered. "
                f"Overwriting with {report_class.__module__}.{report_class.__name__}"
            )

        self._reports[report_class.report_name] = report_class
        logger.debug(f"Registered report: {report_class.report_name}")

        return report_class

    def get(self, report_name: str) -> Type['BaseReport'] | None:
        """Get a report class by name"""
        return self._reports.get(report_name)

    def all(self) -> Dict[str, Type['BaseReport']]:
        """Get all registered reports"""
        return self._reports.copy()

    def clear(self):
        """Clear all registered reports (useful for testing)"""
        self._reports.clear()


# Global registry instance
registry = ReportRegistry()