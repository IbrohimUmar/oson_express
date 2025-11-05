from django.contrib.contenttypes.models import ContentType
from django.forms import model_to_dict

from config.views.login import get_client_ip
from user.models import SystemLog


def log_create(request, created_by_user, instance, action_type=1, extra_details=None, path_url=None):
    details = {"new_values": model_to_dict(instance)}
    if extra_details:
        details.update(extra_details)
    SystemLog.objects.create(
        action=action_type,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.id,
        details=details,
        created_by=created_by_user,
        ip_address=get_client_ip(request) if request is not None else None,
        user_agent=request.META.get("HTTP_USER_AGENT", "") if request is not None else '',
        path=path_url
    )

def log_update(request, created_by_user ,old_instance, new_instance, fields, action_type="1", path_url=None):
    from .helpers import get_changed_fields  # senin fonksiyonun
    changed = get_changed_fields(old_instance, new_instance, fields)
    if not changed:
        return
    SystemLog.objects.create(
        action=action_type,
        content_type=ContentType.objects.get_for_model(new_instance),
        object_id=new_instance.id,
        details=changed,
        created_by=created_by_user,
        ip_address=get_client_ip(request) if request is not None else None,
        user_agent=request.META.get("HTTP_USER_AGENT", "") if request is not None else '',
        path=path_url
    )

def log_delete(request, instance, action_type="1", path_url=None):
    SystemLog.objects.create(
        action=action_type,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.id,
        details={"deleted_values": model_to_dict(instance)},
        created_by=request.user,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        path=path_url
    )
