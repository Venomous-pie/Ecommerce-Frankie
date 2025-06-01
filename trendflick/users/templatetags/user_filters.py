from django import template

register = template.Library()

@register.filter
def calculate_total(items):
    """Calculate total value from a list of items that have a price attribute"""
    return sum(float(item.price) for item in items if hasattr(item, 'price'))

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    return float(value) * float(arg)
