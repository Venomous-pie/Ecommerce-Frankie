from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Split a string into a list using the specified delimiter."""
    return value.split(arg) 