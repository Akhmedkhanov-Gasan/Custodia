from rest_framework.authentication import BaseAuthentication
from django.contrib.auth.models import AnonymousUser

class DjangoUserAuthentication(BaseAuthentication):
    """
    DRF-автентификатор, который доверяет пользователю,
    уже положенному в Django request.user (нашим middleware).
    Никаких заголовков не парсим, токены не трогаем — это делает мидлварь.
    """
    def authenticate(self, request):
        raw = getattr(request, "_request", None)
        user = getattr(raw, "user", None)
        if user and not isinstance(user, AnonymousUser) and user.is_authenticated:
            return (user, None)
        return None
