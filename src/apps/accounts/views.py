# src/apps/accounts/views.py
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny

from .models import Credential
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer
from .utils import (
    hash_password,
    check_password as cred_check_password,
    make_access,
    make_refresh,
    decode_token,
)

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
            email=data["email"].strip().lower(),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            is_active=True,
        )
        user.set_password(data["password"])  # для админки/стандарта Django
        user.save(update_fields=["password"])

        Credential.objects.update_or_create(
            user=user, defaults={"password_hash": hash_password(data["password"])}
        )

        if hasattr(user, "profile") and data.get("patronymic"):
            user.profile.patronymic = data["patronymic"]
            user.profile.save(update_fields=["patronymic"])

        return Response({"id": user.id, "email": user.email}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        identity = s.validated_data.get("email") or s.validated_data.get("username")
        password = s.validated_data["password"]

        identity = (identity or "").strip()
        identity_l = identity.lower()

        try:
            user = (
                    User.objects.filter(email__iexact=identity_l).first()
                    or User.objects.filter(username=identity).first()
            )
        except MultipleObjectsReturned:
            return Response({"detail": "Неверные учетные данные."}, status=400)

        if not user or not user.is_active:
            return Response({"detail": "Неверные учетные данные."}, status=400)

        ok = False
        cred = getattr(user, "cred", None)
        if cred and cred.password_hash:
            try:
                ok = cred_check_password(password, cred.password_hash)
            except Exception:
                ok = False

        if not ok and user.password:
            try:
                ok = user.check_password(password)
            except Exception:
                ok = False

        if not ok:
            return Response({"detail": "Неверные учетные данные."}, status=400)

        return Response({"access": make_access(user.id), "refresh": make_refresh(user.id)}, status=200)


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