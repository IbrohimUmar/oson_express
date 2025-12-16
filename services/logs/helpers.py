


from datetime import datetime
from datetime import datetime, date
from decimal import Decimal


def serialize_value(value):
    if value is None:
        return None

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    if hasattr(value, "id"):
        return value.id

    return str(value)


def get_changed_fields(old_instance, new_instance, fields):
    changed = {}

    for field in fields:
        old_val = getattr(old_instance, field, None)
        new_val = getattr(new_instance, field, None)
        model_field = old_instance._meta.get_field(field)

        # ForeignKey ise sadece ID kaydedelim
        if hasattr(model_field, "remote_field"):
            if hasattr(old_val, "id"):
                old_val = old_val.id
            if hasattr(new_val, "id"):
                new_val = new_val.id

        # Datetime tiplerini string yap
        old_val = serialize_value(old_val)
        new_val = serialize_value(new_val)

        # Değer değişmişse kaydet
        if old_val != new_val:
            changed[field] = {"old": old_val, "new": new_val}

    if not changed:
        return None

    return {
        "changed_fields": changed
    }


