from rest_framework.authentication import BaseAuthentication
from django.contrib.auth.models import AnonymousUser

class DjangoUserAuthentication(BaseAuthentication):
    """DRF authentication backend that trusts the user set by middleware in request.user."""
    def authenticate(self, request):
        raw = getattr(request, "_request", None)
        user = getattr(raw, "user", None)
        if user and not isinstance(user, AnonymousUser) and user.is_authenticated:
            return (user, None)
        return None
