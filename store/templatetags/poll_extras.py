from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def lower(value):
    print('lover')
    return value.lower()