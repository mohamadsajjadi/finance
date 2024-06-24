from django.contrib.auth.backends import ModelBackend
from .models import User


class UsernamePhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, phone_number=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username, phone_number=phone_number)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
