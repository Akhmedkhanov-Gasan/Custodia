# apps/accounts/middleware.py
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from .utils import decode_token

User = get_user_model()

class JWTAuthMiddleware(MiddlewareMixin):
    """Parses 'Authorization: Bearer <JWT>', validates token and populates request.user."""
    def process_request(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION") or ""
        if not auth.lower().startswith("bearer "):
            return

        token = auth.split(" ", 1)[1].strip()
        try:
            payload = decode_token(token)
        except Exception:
            anon = AnonymousUser()
            request.user = anon
            setattr(request, "_cached_user", anon)
            return

        if payload.get("type") != "access":
            anon = AnonymousUser()
            request.user = anon
            setattr(request, "_cached_user", anon)
            return

        user = User.objects.filter(
            id=int(payload.get("sub", 0)), is_active=True
        ).first()

        if user is None:
            anon = AnonymousUser()
            request.user = anon
            setattr(request, "_cached_user", anon)
            return

        request.user = user
        setattr(request, "_cached_user", user)
