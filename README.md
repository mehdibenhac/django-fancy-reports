# Django Fancy Reports

A customizable and extensible reporting framework for Django with built-in support for HTML, PDF, and text output formats.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/django-4.2%2B-green)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Features

- 📄 **Multiple Output Formats** - HTML, PDF, and plain text
- 🎨 **Customizable Themes** - Database-driven visual themes with color schemes and typography
- 🌐 **Bilingual Support** - Built-in LTR/RTL text direction support
- 🔧 **Extensible Base Class** - Simple inheritance-based report creation
- 🔍 **Auto-discovery** - Automatically discovers reports across Django apps
- 📦 **WeasyPrint Integration** - High-quality PDF generation
- 🎯 **Simple Registration** - Decorator-based report registration
- ⚙️ **Database Configuration** - Configure reports, themes, and page formats via admin
- 🛡️ **Security** - Built-in CSS sanitization to prevent XSS attacks
- 🖥️ **CLI Support** - Generate reports from the command line
- 📐 **Flexible Page Formats** - Predefined formats (A4, Letter, A3) with custom margins

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Creating Reports](#creating-reports)
- [Configuration](#configuration)
- [Themes and Styling](#themes-and-styling)
- [URL Structure](#url-structure)
- [Command Line Interface](#command-line-interface)
- [Security](#security)
- [Advanced Usage](#advanced-usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Requirements

- Python 3.10+
- Django 4.2+
- WeasyPrint (for PDF generation)
- html2text (for text output)

### Install from source

```bash
git clone https://github.com/mehdibenhac/django-fancy-reports.git
cd django-fancy-reports
pip install -e .
```

### Install dependencies

```bash
# Basic installation
pip install django

# For PDF support
pip install weasyprint

# For text output
pip install html2text

# Or install all at once
pip install -e ".[dev]"
```

## Quick Start

### 1. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'django_fancy_reports',
]
```

### 2. Include URLs

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path('', include('django_fancy_reports.root_urls')),
]
```

### 3. Run Migrations

```bash
python manage.py migrate
python manage.py fancy_reports_load_fixtures
```

This will create default themes and page formats.

### 4. Create Your First Report

Create a file `reports.py` in your Django app:

```python
# myapp/reports.py
from django_fancy_reports import register, BaseReport

@register
class MyFirstReport(BaseReport):
    """A simple report example"""
    
    display_name = "My First Report"
    description = "This is my first report"
    template_name = "myapp/reports/my_first_report.html"
    
    def load_data(self):
        return {
            'title': 'Hello, Reports!',
            'items': ['Item 1', 'Item 2', 'Item 3'],
        }
```

### 5. Create the Template

Create `myapp/templates/myapp/reports/my_first_report.html`:

```html
{% extends base_template %}

{% block content %}
<h2>{{ data.title }}</h2>

<ul>
    {% for item in data.items %}
    <li>{{ item }}</li>
    {% endfor %}
</ul>

<p>Generated on: {% now "Y-m-d H:i" %}</p>
{% endblock %}
```

### 6. Access Your Report

Start the development server:

```bash
python manage.py runserver
```

Visit:
- **HTML:** `http://localhost:8000/reports/html/myapp.MyFirstReport/`
- **PDF:** `http://localhost:8000/reports/pdf/myapp.MyFirstReport/`
- **Text:** `http://localhost:8000/reports/text/myapp.MyFirstReport/`

## Creating Reports

### Basic Report Structure

```python
from django_fancy_reports import register, BaseReport

@register('invoices.InvoiceReport')  # Explicit name required
class InvoiceReport(BaseReport):
    """Invoice report with customer and line items"""
    
    # Required attributes
    display_name = "Invoice Report"
    template_name = "invoices/reports/invoice.html"
    
    # Optional attributes
    description = "Detailed invoice with customer information"
    allowed_formats = ['html', 'pdf']  # Restrict available formats
    text_direction = 'ltr'  # Default text direction
    
    def load_data(self):
        """
        Load and return data for the report.
        Access self.record_id for the specific record.
        """
        from .models import Invoice
        
        invoice = Invoice.objects.get(pk=self.record_id)
        
        return {
            'invoice': invoice,
            'customer': invoice.customer,
            'line_items': invoice.items.all(),
            'total': invoice.calculate_total(),
        }
```

**Note**: The @register() decorator requires an explicit name. This name is used:

- In URLs: /reports/html/invoices.InvoiceReport/
- In CLI: python manage.py print_report invoices.InvoiceReport
- In database configuration

**Naming Convention**:

- Use app_name.ReportClassName format
- Keep it concise and descriptive
- Avoid special characters

### Report Templates

Templates extend the base template and have access to:

- `report` - The report instance
- `data` - Dictionary returned from `load_data()`
- `theme` - Current theme instance
- `page_format` - Current page format
- `text_direction` - 'ltr' or 'rtl'
- `is_rtl` - Boolean
- `base_template` - Base template path

```html
{% extends base_template %}

{% block content %}
<div class="invoice">
    <h1>Invoice #{{ data.invoice.number }}</h1>
    
    <div class="customer-info">
        <h2>Customer</h2>
        <p>{{ data.customer.name }}</p>
        <p>{{ data.customer.address }}</p>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>Item</th>
                <th>Quantity</th>
                <th>Price</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            {% for item in data.line_items %}
            <tr>
                <td>{{ item.description }}</td>
                <td>{{ item.quantity }}</td>
                <td>{{ item.price }}</td>
                <td>{{ item.total }}</td>
            </tr>
            {% endfor %}
        </tbody>
        <tfoot>
            <tr>
                <td colspan="3">Total:</td>
                <td>{{ data.total }}</td>
            </tr>
        </tfoot>
    </table>
</div>
{% endblock %}
```

### Custom Header and Footer

```html
{% extends base_template %}

{% block header %}
<div class="custom-header">
    <img src="{% static 'logo.png' %}" alt="Logo">
    <h1>{{ report.display_name }}</h1>
</div>
{% endblock %}

{% block content %}
<!-- Your content here -->
{% endblock %}

{% block footer %}
<div class="custom-footer">
    <p>Page generated on {% now "Y-m-d" %}</p>
    <p>© 2026 Your Company</p>
</div>
{% endblock %}
```

## Configuration

### Settings

```python
# settings.py

# URL prefix for reports (default: 'reports')
REPORTS_URL_PREFIX = 'reports'

# Require authentication by default (default: True)
REPORTS_REQUIRE_AUTH = True

# Enable CSS sanitization (default: True)
REPORTS_SANITIZE_CSS = True

# Allow external URLs in CSS (default: False)
REPORTS_ALLOW_EXTERNAL_CSS_URLS = False
```

### Database Configuration

Configure reports through the Django admin interface at `/admin/`:

#### Report Configuration

- **Report Name:** Full name (e.g., `invoices.InvoiceReport`)
- **Display Name:** Human-readable name
- **Theme:** Choose a theme
- **Page Format:** Choose a page format
- **Text Direction:** LTR or RTL
- **Allowed Formats:** List of formats (e.g., `["html", "pdf"]`)
- **Is Active:** Enable/disable the report
- **Require Authentication:** Whether authentication is required
- **Custom CSS:** Report-specific CSS overrides

## Themes and Styling

### Built-in Themes

Django Fancy Reports includes 5 default themes:

1. **Default** - Clean and minimal with neutral colors
2. **Professional Blue** - Corporate theme with blue accents
3. **Modern Green** - Fresh theme with green accents
4. **Classic Monochrome** - Elegant black and white
5. **Arabic Modern** - Optimized for RTL languages

### Creating Custom Themes

Create themes through the Django admin:

1. Go to **Report Themes** → **Add Report Theme**
2. Configure colors, fonts, header/footer
3. Add custom CSS if needed
4. Save and apply to reports

### Custom CSS

Add custom CSS to themes or reports:

```css
/* Custom theme CSS */
.report-content {
    padding: 2rem;
}

.report-content table {
    border: 2px solid var(--primary-color);
}

.report-content table thead {
    background-color: var(--primary-color);
    color: white;
}

/* Use CSS variables from theme */
h1 {
    color: var(--primary-color);
    font-family: var(--heading-font-family);
}
```

### Page Formats

Built-in page formats:

- **A4 Portrait** (210mm × 297mm) - Default
- **A4 Landscape** (297mm × 210mm)
- **Letter Portrait** (8.5" × 11")
- **Letter Landscape** (11" × 8.5")
- **A3 Portrait** (297mm × 420mm)
- **A3 Landscape** (420mm × 297mm)

Configure margins, orientation, and dimensions through the admin.

## URL Structure

Reports are accessible via URLs:

### Patterns

```
/{prefix}/                                          # List all reports
/{prefix}/{format}/{report_name}/                   # Report without record ID
/{prefix}/{format}/{report_name}/{record_id}/       # Report with record ID
```

### Examples

```
http://localhost:8000/reports/
http://localhost:8000/reports/html/invoices.InvoiceReport/
http://localhost:8000/reports/pdf/invoices.InvoiceReport/123/
```

### Query Parameters

Customize reports with query parameters:

- `text_direction` - 'ltr' or 'rtl'
- `theme_id` - Theme ID to use
- `page_format_id` - Page format ID to use

```
http://localhost:8000/reports/pdf/invoices.InvoiceReport/123/?text_direction=rtl&theme_id=2
```

## Command Line Interface

Generate reports from the command line for automation and testing.

### List All Reports

```bash
python manage.py fancy_reports_list
```

### Show Report Information

```bash
python manage.py fancy_reports_info invoices.InvoiceReport
```

### Generate Reports

```bash
# Output to stdout (HTML)
python manage.py fancy_reports_print invoices.InvoiceReport --format html

# Save to file
python manage.py fancy_reports_print invoices.InvoiceReport --format pdf -o invoice.pdf

# With record ID
python manage.py fancy_reports_print invoices.InvoiceReport --record-id 123 --format pdf -o invoice_123.pdf

# With custom theme and page format
python manage.py fancy_reports_print invoices.InvoiceReport --theme 2 --page-format 1 --format pdf -o custom.pdf

# RTL direction
python manage.py fancy_reports_print invoices.InvoiceReport --text-direction rtl --format html -o invoice_ar.html

# Quiet mode (no info messages)
python manage.py fancy_reports_print invoices.InvoiceReport --format pdf -o output.pdf --quiet
```

### Load Fixtures

Load default themes and page formats:

```bash
python manage.py fancy_reports_load_fixtures
```

## Security

### CSS Sanitization

Django Fancy Reports automatically sanitizes custom CSS to prevent XSS and other security vulnerabilities.

The sanitizer removes:
- ✓ Dangerous properties (`behavior`, `expression`, `-moz-binding`)
- ✓ `javascript:`, `data:`, and `vbscript:` URLs
- ✓ `@import` rules
- ✓ Malicious selectors

#### Example

**Dangerous CSS (blocked):**
```css
.evil {
    behavior: url(malicious.htc);
    background: url(javascript:alert('XSS'));
    width: expression(alert('XSS'));
}
```

**Safe CSS (allowed):**
```css
.safe {
    color: #333;
    font-size: 14px;
    background: #fff;
    padding: 1rem;
}
```

#### Configuration

```python
# settings.py

# Enable/disable CSS sanitization (default: True)
REPORTS_SANITIZE_CSS = True

# Allow external URLs in CSS (default: False)
REPORTS_ALLOW_EXTERNAL_CSS_URLS = False
```

### Authentication

Control access to reports:

```python
# settings.py
REPORTS_REQUIRE_AUTH = True  # Global default
```

Or configure per-report in the admin interface.

## Advanced Usage

### Custom Context Data

Override `get_context_data()` to add custom context:

```python
class CustomReport(BaseReport):
    display_name = "Custom Report"
    template_name = "reports/custom.html"
    
    def load_data(self):
        return {'base_data': 'value'}
    
    def get_context_data(self):
        context = super().get_context_data()
        context['extra'] = 'Additional data'
        context['computed'] = self.compute_something()
        return context
    
    def compute_something(self):
        return "Computed value"
```

### Dynamic Template Selection

```python
class DynamicReport(BaseReport):
    display_name = "Dynamic Report"
    
    def get_template_name(self):
        if self.is_rtl:
            return "reports/dynamic_rtl.html"
        return "reports/dynamic_ltr.html"
    
    def load_data(self):
        return {}
```

### Custom Filename

```python
class InvoiceReport(BaseReport):
    display_name = "Invoice"
    template_name = "reports/invoice.html"
    
    def load_data(self):
        invoice = Invoice.objects.get(pk=self.record_id)
        return {'invoice': invoice}
    
    def get_filename(self, format='pdf'):
        invoice = self.data['invoice']
        return f"invoice_{invoice.number}_{invoice.date}.{format}"
```

### Override Rendering

```python
class CustomRenderReport(BaseReport):
    display_name = "Custom Render"
    template_name = "reports/custom.html"
    
    def load_data(self):
        return {}
    
    def render_text(self):
        """Custom text rendering"""
        return f"""
        {self.display_name}
        {'=' * len(self.display_name)}
        
        Custom text output here.
        """
```

## Examples

### Invoice Report

```python
# invoices/reports.py
from django_fancy_reports import register, BaseReport
from .models import Invoice

@register
class InvoiceReport(BaseReport):
    display_name = "Invoice"
    description = "Customer invoice with line items"
    template_name = "invoices/reports/invoice.html"
    allowed_formats = ['html', 'pdf']
    
    def load_data(self):
        invoice = Invoice.objects.select_related('customer').prefetch_related('items').get(
            pk=self.record_id
        )
        
        return {
            'invoice': invoice,
            'customer': invoice.customer,
            'items': invoice.items.all(),
            'subtotal': invoice.calculate_subtotal(),
            'tax': invoice.calculate_tax(),
            'total': invoice.calculate_total(),
        }
```

### Monthly Sales Report

```python
# sales/reports.py
from django_fancy_reports import register, BaseReport
from django.db.models import Sum, Count
from .models import Sale
import datetime

@register
class MonthlySalesReport(BaseReport):
    display_name = "Monthly Sales Report"
    template_name = "sales/reports/monthly.html"
    
    def load_data(self):
        # Get current month by default, or from record_id as YYYYMM
        if self.record_id:
            year = int(self.record_id[:4])
            month = int(self.record_id[4:])
        else:
            today = datetime.date.today()
            year = today.year
            month = today.month
        
        sales = Sale.objects.filter(
            date__year=year,
            date__month=month
        ).aggregate(
            total_amount=Sum('amount'),
            total_count=Count('id')
        )
        
        top_products = Sale.objects.filter(
            date__year=year,
            date__month=month
        ).values('product__name').annotate(
            total=Sum('amount')
        ).order_by('-total')[:10]
        
        return {
            'year': year,
            'month': month,
            'month_name': datetime.date(year, month, 1).strftime('%B'),
            'total_amount': sales['total_amount'] or 0,
            'total_count': sales['total_count'] or 0,
            'top_products': top_products,
        }
```

### RTL Arabic Report

```python
# documents/reports.py
from django_fancy_reports import register, BaseReport

@register('documents.ArabicReport')
class ArabicReport(BaseReport):
    display_name = "تقرير عربي"
    description = "تقرير باللغة العربية"
    template_name = "documents/reports/arabic.html"
    text_direction = 'rtl'  # Default to RTL
    
    def load_data(self):
        return {
            'title': 'عنوان التقرير',
            'content': 'محتوى التقرير هنا',
        }
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/mehdibenhac/django-fancy-reports.git
cd django-fancy-reports

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
cd testproject
python manage.py test django_fancy_reports
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test django_fancy_reports.tests.test_css_sanitizer

# Run with coverage
coverage run --source='django_fancy_reports' manage.py test
coverage report
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Django](https://www.djangoproject.com/)
- PDF generation powered by [WeasyPrint](https://weasyprint.org/)
- Text conversion using [html2text](https://github.com/Alir3z4/html2text/)

## Support

- **Issues:** [GitHub Issues](https://github.com/mehdibenhac/django-fancy-reports/issues)
- **Documentation:** [Coming soon]
- **Email:** mehdi@benhac.com

---

Made with ❤️ by [Mehdi Benhac](https://github.com/mehdibenhac)
