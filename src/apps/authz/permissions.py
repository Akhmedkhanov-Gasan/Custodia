from typing import Optional
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from django.contrib.auth.models import AnonymousUser
from .models import BusinessElement, AccessRoleRule
from django.contrib.auth import get_user_model

User = get_user_model()


def resolve_business_element_code(view) -> Optional[str]:
    return getattr(view, "business_element_code", None)


def get_user_role(user) -> Optional[str]:
    try:
        role = user.profile.role
        return role.code if role else None
    except Exception:
        return None


class RolePermission(BasePermission):
    """RBAC permission that checks AccessRoleRule for a given business_element_code and enforces owner checks."""
    message = "Forbidden by access rules."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            raise NotAuthenticated("Authentication required")

        if not getattr(user, "is_active", False):
            raise NotAuthenticated("Inactive user")

        element_code = resolve_business_element_code(view)
        if not element_code:
            raise PermissionDenied("Business element is not specified")

        role_code = get_user_role(user)
        if not role_code:
            raise PermissionDenied("User has no role")

        try:
            element = BusinessElement.objects.get(code=element_code)
        except BusinessElement.DoesNotExist:
            raise PermissionDenied("Unknown business element")

        rule = AccessRoleRule.objects.filter(
            role__code=role_code, element=element
        ).first()
        if not rule:
            raise PermissionDenied("No rule for role and element")

        method = request.method.upper()
        if method in SAFE_METHODS or method == "GET":
            return bool(rule.read_permission)
        if method == "POST":
            return bool(rule.create_permission)
        if method in ("PUT", "PATCH"):
            return bool(rule.update_permission)
        if method == "DELETE":
            return bool(rule.delete_permission)

        return True

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        element_code = resolve_business_element_code(view)
        role_code = get_user_role(user)

        try:
            element = BusinessElement.objects.get(code=element_code)
            rule = AccessRoleRule.objects.get(role__code=role_code, element=element)
        except Exception:
            raise PermissionDenied("No rule for role and element")

        method = request.method.upper()

        owner_id = getattr(obj, "owner_id", None)
        is_owner = owner_id == getattr(user, "id", None)

        if method in SAFE_METHODS or method == "GET":
            return bool(rule.read_all_permission or is_owner)
        if method in ("PUT", "PATCH"):
            return bool(rule.update_all_permission or (rule.update_permission and is_owner))
        if method == "DELETE":
            return bool(rule.delete_all_permission or (rule.delete_permission and is_owner))

        return True
