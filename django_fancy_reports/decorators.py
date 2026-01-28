from typing import TYPE_CHECKING
from .registry import registry

if TYPE_CHECKING:
    from .base import BaseReport


def register(name: str):
    """
    Decorator to register a report class with the global registry.

    Usage:
        @register('invoices.InvoiceReport')
        class InvoiceReport(BaseReport):
            ...

    Args:
        name: Unique name for the report (e.g., 'invoices.InvoiceReport')

    Returns:
        Decorator function that registers the class

    Raises:
        TypeError: If name is not provided or is not a string
    """
    if not isinstance(name, str):
        raise TypeError(
            f"@register() requires a string name argument. "
            f"Usage: @register('app.ReportName')"
        )

    if not name:
        raise ValueError(
            "Report name cannot be empty. "
            "Usage: @register('app.ReportName')"
        )

    def decorator(cls: type[BaseReport]) -> type[BaseReport]:
        """Inner decorator that performs the registration"""
        return registry.register(name, cls)

    return decorator
