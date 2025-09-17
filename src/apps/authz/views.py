from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from .models import Role, BusinessElement, AccessRoleRule
from .serializers import RoleSerializer, BusinessElementSerializer, AccessRoleRuleSerializer
from .permissions import RolePermission


class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all().order_by("id")
    serializer_class = RoleSerializer
    permission_classes = [RolePermission]
    business_element_code = "rules"


class BusinessElementViewSet(ModelViewSet):
    queryset = BusinessElement.objects.all().order_by("id")
    serializer_class = BusinessElementSerializer
    permission_classes = [RolePermission]
    business_element_code = "rules"


class AccessRoleRuleViewSet(ModelViewSet):
    queryset = AccessRoleRule.objects.select_related("role", "element").all().order_by("id")
    serializer_class = AccessRoleRuleSerializer
    permission_classes = [RolePermission]
    business_element_code = "rules"
