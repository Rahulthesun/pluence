from django.contrib.auth.backends import BaseBackend
from .models import EmailUser

class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = EmailUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except EmailUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return EmailUser.objects.get(pk=user_id)
        except EmailUser.DoesNotExist:
            return None
