
def format_money(value):
    if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
        return "{:,.0f}".format(float(value)).replace(",", " ")
    else:
        return 0