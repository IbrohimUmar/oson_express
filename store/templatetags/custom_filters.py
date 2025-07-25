from django import template

register = template.Library()

@register.filter(name='format_money')
def format_money(value):
    try:
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
            return "{:,.0f}".format(float(value)).replace(",", " ")
        else:
            return 0
    except (ValueError, TypeError):
        return value  # Eğer değer bir sayı değilse olduğu gibi döndür.