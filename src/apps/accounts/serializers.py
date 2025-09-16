from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Credential

User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    password2 = serializers.CharField(min_length=6, write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")
    patronymic = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Пароли не совпадают.")
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("Пользователь с таким email уже есть.")
        return data

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ProfileSerializer(serializers.Serializer):
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")
    patronymic = serializers.CharField(required=False, allow_blank=True, default="")
    is_active = serializers.BooleanField(read_only=True)

    def to_representation(self, instance):
        u = instance
        return {
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "patronymic": getattr(u.profile, "patronymic", ""),
            "is_active": u.is_active,
        }

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save(update_fields=["first_name", "last_name"])
        if "patronymic" in validated_data and hasattr(instance, "profile"):
            instance.profile.patronymic = validated_data["patronymic"]
            instance.profile.save(update_fields=["patronymic"])
        return instance
