from django.db import models
from django.utils.translation import gettext_lazy as _


class ReportPageFormat(models.Model):
    """
    Defines page formats for reports (A4, Letter, etc.)
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Name"),
        help_text=_("e.g., 'A4 Portrait', 'Letter Landscape'")
    )
    width = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_("Width (mm)"),
        help_text=_("Page width in millimeters")
    )
    height = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_("Height (mm)"),
        help_text=_("Page height in millimeters")
    )
    orientation = models.CharField(
        max_length=10,
        choices=[
            ('portrait', _('Portrait')),
            ('landscape', _('Landscape'))
        ],
        default='portrait',
        verbose_name=_("Orientation")
    )
    margin_top = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20,
        verbose_name=_("Top Margin (mm)")
    )
    margin_bottom = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20,
        verbose_name=_("Bottom Margin (mm)")
    )
    margin_left = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20,
        verbose_name=_("Left Margin (mm)")
    )
    margin_right = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20,
        verbose_name=_("Right Margin (mm)")
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Is Default"),
        help_text=_("Only one format can be default")
    )

    class Meta:
        verbose_name = _("Report Page Format")
        verbose_name_plural = _("Report Page Formats")
        ordering = ['name']

    def __str__(self) -> str:
        return f"{self.name} ({self.get_orientation_display()})"

    def save(self, *args, **kwargs) -> None:
        """Ensure only one default format exists"""
        if self.is_default:
            # Set all other formats to non-default
            ReportPageFormat.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def css_page_size(self) -> str:
        """
        Returns CSS @page size declaration for WeasyPrint

        Example output: "size: 210mm 297mm;"
        """
        return f"size: {self.width}mm {self.height}mm;"
