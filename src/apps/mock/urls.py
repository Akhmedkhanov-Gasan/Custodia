from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoodViewSet, OrderViewSet

router = DefaultRouter()
router.register(r"goods", GoodViewSet, basename="mock-goods")
router.register(r"orders", OrderViewSet, basename="mock-orders")

urlpatterns = [path("", include(router.urls))]
