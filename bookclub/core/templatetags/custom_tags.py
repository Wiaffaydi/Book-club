from django import template
register = template.Library()

@register.filter
def get_range(value, arg):
    return range(1, arg+1)

@register.filter
def floatval(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
