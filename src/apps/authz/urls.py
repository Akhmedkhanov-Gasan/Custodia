from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, BusinessElementViewSet, AccessRoleRuleViewSet

router = DefaultRouter()
router.register(r"roles", RoleViewSet, basename="authz-roles")
router.register(r"elements", BusinessElementViewSet, basename="authz-elements")
router.register(r"rules", AccessRoleRuleViewSet, basename="authz-rules")

urlpatterns = [
    path("", include(router.urls)),
]
