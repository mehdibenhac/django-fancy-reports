import logging
from abc import ABC, abstractmethod

from django.template import Template, Context
from django.template.loader import render_to_string
from django.contrib.staticfiles import finders

logger = logging.getLogger(__name__)


class ReportFormat:
    """Constants for report output formats"""
    HTML = 'html'
    PDF = 'pdf'
    TEXT = 'text'

    CHOICES = [
        (HTML, 'HTML'),
        (PDF, 'PDF'),
        (TEXT, 'Text'),
    ]

    @classmethod
    def get_all(cls) -> list[str]:
        """Get list of all format values"""
        return [cls.HTML, cls.PDF, cls.TEXT]


class BaseReport(ABC):
    """
    Base class for all reports.

    Subclasses must implement:
        - load_data() method
        - template_name attribute
        - display_name attribute
    """

    # === Required Attributes ===
    report_name: str | None = None
    display_name: str | None = None
    template_name: str | None = None

    # === Optional Metadata ===
    description: str = ""
    text_direction: str = 'ltr'

    # Database configuration (optional)
    theme: str | None = None  # Theme name or None
    page_format: str | None = None  # Page format name or None
    custom_css: str = ""

    def __init__(
            self,
            record_id: str | int | None = None,
            text_direction: str | None = None,
            theme_instance=None,
            page_format_instance=None,
    ) -> None:
        """
        Initialize report instance.

        Args:
            record_id: ID of the record to generate report for
            text_direction: 'ltr' or 'rtl'
            theme_instance: ReportTheme instance or ID
            page_format_instance: ReportPageFormat instance or ID
        """
        self.record_id = record_id
        self._text_direction = text_direction or self.text_direction
        self._theme = self._resolve_theme(theme_instance)
        self._page_format = self._resolve_page_format(page_format_instance)
        self.data: dict | None = None

    def _resolve_theme(self, theme_instance):
        """
        Resolve theme from various input types.

        Args:
            theme_instance: ReportTheme instance, ID, or None

        Returns:
            ReportTheme instance or None
        """
        from .models import ReportTheme, Report

        # If already a theme instance, return it
        if theme_instance is not None and hasattr(theme_instance,
                                                  '__class__') and theme_instance.__class__.__name__ == 'ReportTheme':
            return theme_instance

        # If it's an ID, fetch from database
        if isinstance(theme_instance, int):
            return ReportTheme.objects.filter(pk=theme_instance, is_active=True).first()

        # Try to get theme from Report model configuration
        if self.report_name:
            try:
                report_config = Report.objects.get(report_name=self.report_name)
                if report_config.theme:
                    return report_config.theme
            except Report.DoesNotExist:
                pass

        # Try to get theme by name from class attribute
        if self.theme:
            theme_obj = ReportTheme.objects.filter(
                name=self.theme,
                is_active=True
            ).first()
            if theme_obj:
                return theme_obj

        # Fall back to default theme
        return ReportTheme.objects.filter(is_default=True, is_active=True).first()

    def _resolve_page_format(self, page_format_instance):
        """
        Resolve page format from various input types.

        Args:
            page_format_instance: ReportPageFormat instance, ID, or None

        Returns:
            ReportPageFormat instance or None
        """
        from .models import ReportPageFormat, Report

        # If already a page format instance, return it
        if page_format_instance is not None and hasattr(page_format_instance,
                                                        '__class__') and page_format_instance.__class__.__name__ == 'ReportPageFormat':
            return page_format_instance

        # If it's an ID, fetch from database
        if isinstance(page_format_instance, int):
            return ReportPageFormat.objects.filter(pk=page_format_instance).first()

        # Try to get page format from Report model configuration
        if self.report_name:
            try:
                report_config = Report.objects.get(report_name=self.report_name)
                if report_config.page_format:
                    return report_config.page_format
            except Report.DoesNotExist:
                pass

        # Try to get page format by name from class attribute
        if self.page_format:
            format_obj = ReportPageFormat.objects.filter(
                name=self.page_format
            ).first()
            if format_obj:
                return format_obj

        # Fall back to default page format
        return ReportPageFormat.objects.filter(is_default=True).first()

    @property
    def is_rtl(self) -> bool:
        """Check if report uses right-to-left text direction"""
        return self._text_direction == 'rtl'

    @property
    def resolved_theme(self):
        """Get the resolved theme instance"""
        return self._theme

    @property
    def resolved_page_format(self):
        """Get the resolved page format instance"""
        return self._page_format

    @abstractmethod
    def load_data(self) -> dict:
        """
        Load and return data for the report.
        Must be implemented by subclasses.

        Returns:
            dict: Context data for template rendering
        """
        pass

    def get_context_data(self) -> dict:
        """
        Get complete context data for template rendering.
        Can be overridden to add additional context.

        Returns:
            dict: Complete context dictionary
        """
        if self.data is None:
            self.data = self.load_data()

        context = {
            'report': self,
            'data': self.data,
            'theme': self._theme,
            'page_format': self._page_format,
            'text_direction': self._text_direction,
            'is_rtl': self.is_rtl,
        }

        return context

    def get_template_name(self) -> str:
        """
        Get template name for rendering.
        Can be overridden for dynamic template selection.

        Returns:
            str: Template path

        Raises:
            NotImplementedError: If template_name is not defined
        """
        if not self.template_name:
            raise NotImplementedError(
                f"template_name must be defined for {self.__class__.__name__}"
            )
        return self.template_name

    def get_base_template(self) -> str:
        """
        Get base template path.

        Returns:
            str: Base template path
        """
        return 'django_fancy_reports/base_report.html'

    def _render_css_template(self, css_content: str, context: dict) -> str:
        """
        Render CSS content as a Django template.

        Args:
            css_content: CSS string that may contain template variables
            context: Context dictionary for rendering

        Returns:
            str: Rendered CSS
        """
        try:
            template = Template(css_content)
            return template.render(Context(context))
        except Exception as e:
            logger.warning(f"Error rendering CSS template: {e}")
            return css_content

    def get_stylesheets(self) -> list[str]:
        """
        Compile and return all stylesheets for the report.

        Returns:
            list: List of CSS strings
        """
        from .models import Report

        stylesheets = []

        # Get context for CSS rendering
        css_context = {
            'text_direction': self._text_direction,
            'is_rtl': self.is_rtl,
            'theme': self._theme,
            'page_format': self._page_format,
        }

        # 1. Base framework CSS (static)
        base_css = self._load_static_css('django_fancy_reports/css/base.css')
        if base_css:
            stylesheets.append(base_css)

        # 2. Dynamic direction CSS (rendered as template)
        direction_css = render_to_string(
            'django_fancy_reports/css/direction.css',
            css_context
        )
        stylesheets.append(direction_css)

        # 3. Theme CSS (rendered as template to support variables)
        if self._theme:
            theme_css = self._theme.get_css_variables()
            stylesheets.append(theme_css)

        # 4. Report-specific CSS from database (rendered as template)
        if self.report_name:
            try:
                report_config = Report.objects.get(report_name=self.report_name)
                if report_config.custom_css:
                    custom_css = report_config.get_compiled_css()
                    rendered_custom_css = self._render_css_template(custom_css, css_context)
                    stylesheets.append(rendered_custom_css)
            except Report.DoesNotExist:
                # Fall back to class-level custom CSS
                if self.custom_css:
                    rendered_custom_css = self._render_css_template(self.custom_css, css_context)
                    stylesheets.append(rendered_custom_css)

        # 5. Page format CSS (rendered as template)
        if self._page_format:
            page_css = f"""
            @page {{
                {self._page_format.css_page_size}
                margin-top: {self._page_format.margin_top}mm;
                margin-bottom: {self._page_format.margin_bottom}mm;
                margin-left: {self._page_format.margin_left}mm;
                margin-right: {self._page_format.margin_right}mm;
            }}
            """
            stylesheets.append(page_css)

        return stylesheets

    def _load_static_css(self, path: str) -> str:
        """
        Load CSS from static files.

        Args:
            path: Static file path

        Returns:
            str: CSS content or empty string if not found
        """
        absolute_path = finders.find(path)
        if absolute_path:
            try:
                with open(absolute_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Error loading static CSS {path}: {e}")
        return ""

    def render_html(self) -> str:
        """
        Render report as HTML.

        Returns:
            str: Rendered HTML
        """
        context = self.get_context_data()
        context['base_fancy_report'] = self.get_base_template()
        context['stylesheets'] = self.get_stylesheets()

        return render_to_string(self.get_template_name(), context)

    def render_pdf(self) -> bytes:
        """
        Render report as PDF using WeasyPrint.

        Returns:
            bytes: PDF content
        """
        try:
            from weasyprint import HTML, CSS
        except ImportError:
            raise ImportError(
                "WeasyPrint is required for PDF generation. "
                "Install it with: pip install weasyprint"
            )

        html_content = self.render_html()

        # Create WeasyPrint HTML object
        html_obj = HTML(string=html_content)

        # Prepare CSS stylesheets
        css_list = []
        stylesheets = self.get_stylesheets()
        if stylesheets:
            for stylesheet in stylesheets:
                if isinstance(stylesheet, str):
                    css_list.append(CSS(string=stylesheet))

        # Generate PDF and return bytes directly
        pdf_bytes = html_obj.write_pdf(stylesheets=css_list)

        return pdf_bytes

    def render_text(self) -> str:
        """
        Render report as plain text.
        Can be overridden for custom text rendering.

        Returns:
            str: Plain text content
        """
        try:
            from html2text import html2text
        except ImportError:
            raise ImportError(
                "html2text is required for text generation. "
                "Install it with: pip install html2text"
            )

        html_content = self.render_html()
        return html2text(html_content)

    def render(self, output_format: str = ReportFormat.HTML) -> bytes | str:
        """
        Render report in specified format.

        Args:
            output_format: One of ReportFormat constants

        Returns:
            bytes or str: Rendered content

        Raises:
            ValueError: If format is invalid
        """
        if output_format == ReportFormat.HTML:
            return self.render_html()
        elif output_format == ReportFormat.PDF:
            return self.render_pdf()
        elif output_format == ReportFormat.TEXT:
            return self.render_text()
        else:
            raise ValueError(f"Unknown format: {output_format}")

    def get_filename(self, output_format: str = ReportFormat.PDF) -> str:
        """
        Get filename for downloaded report.
        Can be overridden for custom naming.

        Args:
            output_format: Report format

        Returns:
            str: Filename with extension
        """
        from django.utils.text import slugify

        name = slugify(self.display_name or self.report_name or 'report')
        extension = output_format.lower()

        if self.record_id:
            return f"{name}_{self.record_id}.{extension}"
        return f"{name}.{extension}"
