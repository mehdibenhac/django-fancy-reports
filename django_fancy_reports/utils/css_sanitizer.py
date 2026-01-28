import re
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class CSSSanitizer:
    """
    Sanitize CSS to prevent XSS and other security vulnerabilities.

    This sanitizer:
    - Removes dangerous properties (like 'behavior', 'expression', '-moz-binding')
    - Removes javascript: URLs
    - Removes @import rules that could load external resources
    - Validates color values
    - Removes invalid/malicious selectors
    """

    # Dangerous CSS properties that can execute code
    DANGEROUS_PROPERTIES = [
        'behavior',
        'expression',
        '-moz-binding',
        'binding',
    ]

    # Dangerous URL schemes
    DANGEROUS_URL_SCHEMES = [
        'javascript:',
        'data:',
        'vbscript:',
    ]

    # Allowed @ rules
    ALLOWED_AT_RULES = [
        '@page',
        '@media',
        '@font-face',
        '@keyframes',
        '@-webkit-keyframes',
        '@-moz-keyframes',
    ]

    def __init__(self, allow_external_urls: bool = False):
        """
        Initialize sanitizer.

        Args:
            allow_external_urls: If True, allows http(s) URLs. Default: False
        """
        self.allow_external_urls = allow_external_urls

    def sanitize(self, css: str) -> str:
        """
        Sanitize CSS string.

        Args:
            css: CSS string to sanitize

        Returns:
            str: Sanitized CSS
        """
        if not css or not css.strip():
            return ""

        # Remove comments
        css = self._remove_comments(css)

        # Remove dangerous @ rules
        css = self._remove_dangerous_at_rules(css)

        # Remove dangerous properties
        css = self._remove_dangerous_properties(css)

        # Sanitize URLs
        css = self._sanitize_urls(css)

        # Remove empty rules
        css = self._remove_empty_rules(css)

        return css.strip()

    def _remove_comments(self, css: str) -> str:
        """Remove CSS comments"""
        return re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)

    def _remove_dangerous_at_rules(self, css: str) -> str:
        """
        Remove dangerous @ rules like @import.
        Keep only allowed @ rules.
        """
        # Pattern to match @ rules
        at_rule_pattern = r'@[a-zA-Z-]+[^{;]*[{;]'

        def check_at_rule(match):
            rule = match.group(0)
            rule_name = rule.split()[0].split('(')[0].split('{')[0]

            # Check if it's an allowed @ rule
            if any(allowed in rule_name.lower() for allowed in self.ALLOWED_AT_RULES):
                return rule

            # Log removal
            logger.warning(f"Removed dangerous @ rule: {rule_name}")
            return ''

        return re.sub(at_rule_pattern, check_at_rule, css)

    def _remove_dangerous_properties(self, css: str) -> str:
        """Remove dangerous CSS properties"""
        # Pattern to match CSS property: value pairs
        property_pattern = r'([a-zA-Z-]+)\s*:\s*([^;]+);'

        def check_property(match):
            property_name = match.group(1).lower().strip()
            property_value = match.group(2).strip()

            # Check if property is dangerous
            if property_name in self.DANGEROUS_PROPERTIES:
                logger.warning(f"Removed dangerous property: {property_name}")
                return ''

            # Check for expression() in value (IE specific vulnerability)
            if 'expression(' in property_value.lower():
                logger.warning(f"Removed expression() in {property_name}")
                return ''

            return match.group(0)

        return re.sub(property_pattern, check_property, css)

    def _sanitize_urls(self, css: str) -> str:
        """Sanitize URLs in CSS"""
        # Pattern to match url() values
        url_pattern = r'url\s*\(\s*["\']?([^)"\'\s]+)["\']?\s*\)'

        def check_url(match):
            url = match.group(1).strip()
            url_lower = url.lower()

            # Check for dangerous URL schemes
            for scheme in self.DANGEROUS_URL_SCHEMES:
                if url_lower.startswith(scheme):
                    logger.warning(f"Removed dangerous URL: {url}")
                    return 'url(about:blank)'

            # Check for external URLs if not allowed
            if not self.allow_external_urls:
                if url_lower.startswith('http://') or url_lower.startswith('https://'):
                    logger.warning(f"Removed external URL: {url}")
                    return 'url(about:blank)'

            return match.group(0)

        return re.sub(url_pattern, check_url, css, flags=re.IGNORECASE)

    def _remove_empty_rules(self, css: str) -> str:
        """Remove CSS rules with empty or whitespace-only bodies"""
        # Pattern to match CSS rules
        rule_pattern = r'([^{]+)\{\s*\}'

        return re.sub(rule_pattern, '', css)

    def validate_selector(self, selector: str) -> bool:
        """
        Validate a CSS selector to ensure it's safe.

        Args:
            selector: CSS selector string

        Returns:
            bool: True if valid, False otherwise
        """
        if not selector or not selector.strip():
            return False

        # Check for dangerous characters
        dangerous_chars = ['<', '>', '\\']
        if any(char in selector for char in dangerous_chars):
            return False

        # Check for script injection attempts
        if 'javascript:' in selector.lower():
            return False

        return True

    def validate_color(self, color: str) -> bool:
        """
        Validate a color value.

        Args:
            color: Color string (hex, rgb, rgba, named color, etc.)

        Returns:
            bool: True if valid, False otherwise
        """
        color = color.strip().lower()

        # Hex color (#fff, #ffffff)
        if re.match(r'^#[0-9a-f]{3}([0-9a-f]{3})?$', color):
            return True

        # RGB/RGBA
        if re.match(r'^rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(,\s*[\d.]+\s*)?\)$', color):
            return True

        # HSL/HSLA
        if re.match(r'^hsla?\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*(,\s*[\d.]+\s*)?\)$', color):
            return True

        # Named colors (basic validation - just check it's alphanumeric)
        if re.match(r'^[a-z]+$', color):
            return True

        return False


# Global sanitizer instance
_sanitizer = CSSSanitizer(allow_external_urls=False)


def sanitize_css(css: str, allow_external_urls: bool = False) -> str:
    """
    Sanitize CSS string.

    Args:
        css: CSS string to sanitize
        allow_external_urls: If True, allows http(s) URLs

    Returns:
        str: Sanitized CSS
    """
    if allow_external_urls:
        sanitizer = CSSSanitizer(allow_external_urls=True)
        return sanitizer.sanitize(css)

    return _sanitizer.sanitize(css)


def validate_color(color: str) -> bool:
    """
    Validate a color value.

    Args:
        color: Color string

    Returns:
        bool: True if valid, False otherwise
    """
    return _sanitizer.validate_color(color)


def validate_selector(selector: str) -> bool:
    """
    Validate a CSS selector.

    Args:
        selector: CSS selector string

    Returns:
        bool: True if valid, False otherwise
    """
    return _sanitizer.validate_selector(selector)
