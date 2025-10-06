from django import template

register = template.Library()


@register.filter(name='startswith')
def startswith_filter(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False


@register.filter(name='format_money')
def format_money(value):
    try:
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
            return "{:,.0f}".format(float(value)).replace(",", " ")
        else:
            return 0
    except (ValueError, TypeError):
        return value  # Eğer değer bir sayı değilse olduğu gibi döndür.


