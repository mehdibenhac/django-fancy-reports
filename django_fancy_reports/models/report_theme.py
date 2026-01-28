# django_fancy_reports/models/theme.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class ReportTheme(models.Model):
    """
    Defines visual themes for reports using CSS variables.
    Only controls colors, fonts, and background - does not override layout/structure.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Name")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )

    # Color Scheme
    primary_color = models.CharField(
        max_length=7,
        default='#0F172A',
        verbose_name=_("Primary Color"),
        help_text=_("Main text and headings color (e.g., #333333)")
    )
    secondary_color = models.CharField(
        max_length=7,
        default='#666666',
        verbose_name=_("Secondary Color"),
        help_text=_("Secondary text color")
    )
    background_color = models.CharField(
        max_length=7,
        default='#ffffff',
        verbose_name=_("Background Color")
    )
    border_color = models.CharField(
        max_length=7,
        default='#dddddd',
        verbose_name=_("Border Color"),
        help_text=_("Table borders and dividers")
    )
    header_bg_color = models.CharField(
        max_length=7,
        default='#f5f5f5',
        verbose_name=_("Table Header Background"),
        help_text=_("Background color for table headers")
    )

    # Typography
    font_family = models.CharField(
        max_length=200,
        default="'Helvetica Neue', Arial, sans-serif",
        verbose_name=_("Font Family"),
        help_text=_("Main font family for the report")
    )

    # Table Row Colors
    row_even_bg_color = models.CharField(
        max_length=7,
        default='#ffffff',
        verbose_name=_("Even Row Background"),
        help_text=_("Background color for even rows (2nd, 4th, etc.)")
    )
    row_odd_bg_color = models.CharField(
        max_length=7,
        default='#f9f9f9',
        verbose_name=_("Odd Row Background"),
        help_text=_("Background color for odd rows (1st, 3rd, etc.)")
    )

    # Background Image
    background_image = models.ImageField(
        upload_to='report_themes/backgrounds/',
        blank=True,
        null=True,
        verbose_name=_("Background Image"),
        help_text=_("Optional background image for the report")
    )
    background_image_opacity = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.05,
        validators=[MinValueValidator(0.01), MaxValueValidator(1.00)],
        verbose_name=_("Background Image Opacity"),
        help_text=_("Opacity of background image (0.01 to 1.00). Lower is more subtle.")
    )
    background_image_position = models.CharField(
        max_length=50,
        default='center',
        verbose_name=_("Background Image Position"),
        choices=[
            ('center', _('Center')),
            ('top', _('Top')),
            ('bottom', _('Bottom')),
            ('left', _('Left')),
            ('right', _('Right')),
            ('top left', _('Top Left')),
            ('top right', _('Top Right')),
            ('bottom left', _('Bottom Left')),
            ('bottom right', _('Bottom Right')),
        ],
        help_text=_("Position of the background image")
    )
    background_image_size = models.CharField(
        max_length=50,
        default='cover',
        verbose_name=_("Background Image Size"),
        choices=[
            ('cover', _('Cover (fill container)')),
            ('contain', _('Contain (fit inside)')),
            ('auto', _('Auto (original size)')),
            ('50%', _('50% of container')),
            ('100%', _('100% of container')),
        ],
        help_text=_("How the background image should be sized")
    )
    background_image_repeat = models.CharField(
        max_length=20,
        default='no-repeat',
        verbose_name=_("Background Image Repeat"),
        choices=[
            ('no-repeat', _('No Repeat')),
            ('repeat', _('Repeat')),
            ('repeat-x', _('Repeat Horizontally')),
            ('repeat-y', _('Repeat Vertically')),
        ],
        help_text=_("Whether the background image should repeat")
    )

    # Status
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Is Default"),
        help_text=_("Only one theme can be default")
    )

    class Meta:
        verbose_name = _("Report Theme")
        verbose_name_plural = _("Report Themes")
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Ensure only one default theme exists"""
        if self.is_default:
            ReportTheme.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def get_css_variables(self) -> str:
        """
        Returns CSS with only variable overrides.
        Does NOT include any layout or structural CSS.
        """
        css = f"""
/* Theme: {self.name} */
:root {{
    --report-primary-color: {self.primary_color};
    --report-secondary-color: {self.secondary_color};
    --report-background: {self.background_color};
    --report-border-color: {self.border_color};
    --report-header-bg: {self.header_bg_color};
    --report-font-family: {self.font_family};
    --report-row-even-bg: {self.row_even_bg_color};
    --report-row-odd-bg: {self.row_odd_bg_color};
}}
"""

        # Add background image styles if an image is set
        if self.background_image:
            css += f"""
body {{
    position: relative;
}}

body::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url('{self.background_image.url}');
    background-position: {self.background_image_position};
    background-size: {self.background_image_size};
    background-repeat: {self.background_image_repeat};
    opacity: {self.background_image_opacity};
    z-index: -1;
    pointer-events: none;
}}
"""

        return css.strip()