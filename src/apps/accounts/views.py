from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions

from .models import Credential
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer
from .utils import hash_password, check_password, make_access, make_refresh, decode_token

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        user = User.objects.create(
            username=data["email"],
            email=data["email"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            is_active=True,
        )
        Credential.objects.create(user=user, password_hash=hash_password(data["password"]))
        if hasattr(user, "profile") and data.get("patronymic"):
            user.profile.patronymic = data["patronymic"]
            user.profile.save(update_fields=["patronymic"])
        return Response({"id": user.id, "email": user.email}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        email = s.validated_data["email"]
        password = s.validated_data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Неверные учетные данные."}, status=400)

        if not user.is_active:
            return Response({"detail": "Аккаунт деактивирован."}, status=403)

        cred = getattr(user, "cred", None)
        if not cred or not check_password(password, cred.password_hash):
            return Response({"detail": "Неверные учетные данные."}, status=400)

        return Response({
            "access": make_access(user.id),
            "refresh": make_refresh(user.id),
        })

class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("refresh")
        if not token:
            return Response({"detail": "refresh токен обязателен"}, status=400)
        try:
            payload = decode_token(token)
        except Exception:
            return Response({"detail": "Неверный или истекший токен."}, status=401)
        if payload.get("type") != "refresh":
            return Response({"detail": "Неверный тип токена."}, status=400)
        user_id = int(payload["sub"])
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден или деактивирован."}, status=401)
        return Response({"access": make_access(user.id)})

class LogoutView(APIView):
    def post(self, request):
        return Response({"detail": "ok"})

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data)

    def patch(self, request):
        s = ProfileSerializer(instance=request.user, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(ProfileSerializer(request.user).data)

    def delete(self, request):
        u = request.user
        u.is_active = False
        u.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)

# Debug
from rest_framework.permissions import AllowAny

class WhoAmIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        u = getattr(request, "user", None)
        return Response({
            "has_authorization_header": bool(request.META.get("HTTP_AUTHORIZATION")),
            "is_authenticated": bool(getattr(u, "is_authenticated", False)),
            "user_id": getattr(u, "id", None),
            "email": getattr(u, "email", None),
            "class": u.__class__.__name__ if u else None,
        })
