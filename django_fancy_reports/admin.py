from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.utils.html import format_html

from .models import ReportPageFormat, ReportTheme, Report
from .utils.css_sanitizer import sanitize_css


@admin.register(ReportPageFormat)
class ReportPageFormatAdmin(admin.ModelAdmin):
    """Admin interface for ReportPageFormat"""

    list_display = [
        'name',
        'dimensions',
        'orientation',
        'margins_display',
        'is_default',
    ]
    list_filter = ['orientation', 'is_default']
    search_fields = ['name']
    readonly_fields = ['css_page_size']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'orientation', 'is_default')
        }),
        ('Dimensions', {
            'fields': ('width', 'height'),
            'description': 'Page dimensions in millimeters'
        }),
        ('Margins', {
            'fields': ('margin_top', 'margin_bottom', 'margin_left', 'margin_right'),
            'description': 'Margins in millimeters'
        }),
        ('Preview', {
            'fields': ('css_page_size',),
            'classes': ('collapse',)
        }),
    )

    def dimensions(self, obj):
        """Display dimensions in a readable format"""
        return f"{obj.width}mm × {obj.height}mm"

    dimensions.short_description = "Dimensions"

    def margins_display(self, obj):
        """Display margins in a readable format"""
        return f"T:{obj.margin_top} R:{obj.margin_right} B:{obj.margin_bottom} L:{obj.margin_left}"

    margins_display.short_description = "Margins (mm)"

    def save_model(self, request, obj, form, change):
        """Override to ensure only one default exists"""
        if obj.is_default:
            ReportPageFormat.objects.filter(is_default=True).update(is_default=False)
        super().save_model(request, obj, form, change)


@admin.register(ReportTheme)
class ReportThemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'has_background_image', 'background_image_opacity']
    list_filter = ['is_default']
    search_fields = ['name', 'description']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_default')
        }),
        ('Colors', {
            'fields': (
                'primary_color',
                'secondary_color',
                'background_color',
                'border_color',
                'header_bg_color',
            )
        }),
        ('Typography', {
            'fields': ('font_family',)
        }),
        ('Tables', {
            'fields': (
                'row_even_bg_color',
                'row_odd_bg_color'
            )
        }),
        ('Background Image', {
            'fields': (
                'background_image',
                'background_image_opacity',
                'background_image_position',
                'background_image_size',
                'background_image_repeat',
            ),
            'classes': ('collapse',),
        }),
    )

    def has_background_image(self, obj):
        return bool(obj.background_image)

    has_background_image.boolean = True
    has_background_image.short_description = 'Has Background'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin interface for Report"""

    list_display = [
        'display_name',
        'report_name',
        'text_direction',
    ]
    list_filter = ['text_direction']
    search_fields = ['report_name', 'display_name', 'description']
    readonly_fields = ['preview_css']

    fieldsets = (
        ('Basic Information', {
            'fields': ('report_name', 'display_name', 'description')
        }),
        ('Configuration', {
            'fields': ('theme', 'page_format', 'text_direction')
        }),
        ('Custom CSS', {
            'fields': ('custom_css',),
            'classes': ('collapse',)
        }),
        ('Preview', {
            'fields': ('preview_css',),
            'classes': ('collapse',)
        }),
    )

    def preview_css(self, obj):
        """Display compiled CSS preview"""
        css = obj.get_compiled_css()
        if not css:
            return format_html('<em>No custom CSS</em>')

        return format_html(
            '<pre style="background:#f5f5f5;padding:10px;'
            'max-height:400px;overflow:auto;">{}</pre>',
            css[:1000] + ('...' if len(css) > 1000 else '')
        )

    def save_model(self, request, obj, form, change):
        """Override to show warning if CSS was sanitized"""
        if obj.custom_css:
            original = obj.custom_css
            if sanitize_css(original) != original:
                messages.warning(
                    request,
                    "Custom CSS was sanitized. Some potentially dangerous content was removed. "
                    "Please review the changes."
                )

        super().save_model(request, obj, form, change)

    preview_css.short_description = "Compiled CSS Preview"

class ReportsAdminSite(AdminSite):
    """Custom admin site for Django Fancy Reports"""
    site_header = "Django Fancy Reports Administration"
    site_title = "Reports Admin"
    index_title = "Manage Reports, Themes, and Formats"

reports_admin_site = ReportsAdminSite(name='reports_admin')
