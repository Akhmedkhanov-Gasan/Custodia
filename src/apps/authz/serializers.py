from rest_framework import serializers
from .models import Role, BusinessElement, AccessRoleRule


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "code", "name"]


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = ["id", "code", "name"]


class AccessRoleRuleSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(
        slug_field="code", queryset=Role.objects.all()
    )
    element = serializers.SlugRelatedField(
        slug_field="code", queryset=BusinessElement.objects.all()
    )

    class Meta:
        model = AccessRoleRule
        fields = [
            "id",
            "role",
            "element",
            "read_permission",
            "read_all_permission",
            "create_permission",
            "update_permission",
            "update_all_permission",
            "delete_permission",
            "delete_all_permission",
        ]
