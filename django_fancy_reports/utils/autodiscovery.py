import logging
from importlib import import_module

from django.apps import apps

logger = logging.getLogger(__name__)


def autodiscover():
    """
    Auto-discover and register all BaseReport subclasses from installed apps.

    Looks for 'reports.py' or 'reports/*.py' modules in each installed app.
    """
    from ..base import BaseReport
    from ..registry import registry

    discovered_count = 0

    for app_config in apps.get_app_configs():
        # Try to import reports module
        module_names = [
            f"{app_config.name}.reports",
        ]

        for module_name in module_names:
            try:
                module = import_module(module_name)

                # Find all BaseReport subclasses in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    # Check if it's a BaseReport subclass (but not BaseReport itself)
                    if (
                            isinstance(attr, type) and
                            issubclass(attr, BaseReport) and
                            attr is not BaseReport and
                            attr.report_name  # Must have report_name defined
                    ):
                        registry.register(attr)
                        discovered_count += 1
                        logger.info(f"Auto-discovered report: {attr.report_name}")

            except ImportError:
                # No reports module in this app, skip it
                continue
            except Exception as e:
                logger.error(f"Error auto-discovering reports in {module_name}: {e}")

    logger.info(f"Auto-discovery complete: {discovered_count} reports registered")
