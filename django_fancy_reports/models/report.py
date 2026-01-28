from django.db import models
from django.utils.translation import gettext_lazy as _

from ..utils.css_sanitizer import sanitize_css


class Report(models.Model):
    """
    Stores report metadata and configuration
    Links registered report classes to database configuration
    """

    TEXT_DIRECTION_CHOICES = [
        ('ltr', _('Left-to-Right')),
        ('rtl', _('Right-to-Left')),
    ]

    report_name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name=_("Report Name"),
        help_text=_("Full report name (e.g., 'invoices.InvoiceReport')")
    )
    display_name = models.CharField(
        max_length=200,
        verbose_name=_("Display Name"),
        help_text=_("Human-readable name for the report")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )

    theme = models.ForeignKey(
        'django_fancy_reports.ReportTheme',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
        verbose_name=_("Theme")
    )
    page_format = models.ForeignKey(
        'django_fancy_reports.ReportPageFormat',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
        verbose_name=_("Page Format")
    )

    text_direction = models.CharField(
        max_length=3,
        choices=TEXT_DIRECTION_CHOICES,
        default='ltr',
        verbose_name=_("Text Direction"),
        help_text=_("Text direction for the report")
    )

    custom_css = models.TextField(
        blank=True,
        verbose_name=_("Custom CSS"),
        help_text=_("Report-specific CSS. Will be sanitized before use.")
    )

    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        ordering = ['report_name']

    def __str__(self) -> str:
        return self.display_name or self.report_name

    @property
    def is_rtl(self) -> bool:
        """Convenience property to check if report is RTL"""
        return self.text_direction == 'rtl'

    def get_compiled_css(self) -> str:
        """Returns sanitized custom CSS for this report"""
        return sanitize_css(self.custom_css) if self.custom_css else ""
