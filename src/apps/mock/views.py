from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import QuerySet

from apps.authz.models import AccessRoleRule, BusinessElement
from apps.authz.permissions import RolePermission
from .models import Good, Order
from .serializers import GoodSerializer, OrderSerializer

def _get_rule(user, element_code: str) -> AccessRoleRule | None:
    role = getattr(getattr(user, "profile", None), "role", None)
    if not role:
        return None
    try:
        element = BusinessElement.objects.get(code=element_code)
    except BusinessElement.DoesNotExist:
        return None
    return AccessRoleRule.objects.filter(role=role, element=element).first()

class GoodViewSet(ModelViewSet):
    queryset = Good.objects.all().order_by("-id")
    serializer_class = GoodSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    business_element_code = "goods"

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        rule = _get_rule(self.request.user, self.business_element_code)
        if not rule or not rule.read_all_permission:
            return qs.filter(owner_id=self.request.user.id)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all().order_by("-id")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    business_element_code = "orders"

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        rule = _get_rule(self.request.user, self.business_element_code)
        if not rule or not rule.read_all_permission:
            return qs.filter(owner_id=self.request.user.id)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
