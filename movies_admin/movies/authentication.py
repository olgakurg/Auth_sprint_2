import requests
from django.contrib.auth.models import User
from django.http import HttpResponse
from ..config import settings


class EmailAuthBackend:
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                response = requests.get(
                    f'http://{settings.AUTH_HOST}:{settings.AUTH_PORT}/{settings.AUTH_API_ROUTE}',
                    params={"login": username, "password": password}
                )
                if response.status_code in (200, 500):
                    return user
                else:
                    return HttpResponse(status=response.status_code)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
