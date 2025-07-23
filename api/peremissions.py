from rest_framework import permissions

from user.models import User

MyToken = "asdA2D21kwo12oasdWALKSAMD.KA2KSMaslkdalsjdlkasdALDKMAaskdalskdlasdlkasmldsadasdas"

class MyTokenPermission(permissions.BasePermission):
    details = 'Siz tokenini hato kiritdingiz'
    def has_permission(self, request, view):
        if request.headers.get('MyToken') == str(MyToken):
            return True
        else:
            return False


class BotChatIdPermission(permissions.BasePermission):
    message = "Chat id not'g'ri"
    def has_permission(self, request, view):
        user = User.objects.filter(tg_user_id=int(request.headers.get('ChatId')), is_active=True).first()
        if user:
            request.user = user
            return True
        else:
            return False

