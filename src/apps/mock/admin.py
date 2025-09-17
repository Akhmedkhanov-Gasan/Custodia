from django.contrib import admin
from .models import Good, Order

@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "created_at")
    list_filter = ("owner",)
    search_fields = ("title",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "number", "owner", "created_at")
    list_filter = ("owner",)
    search_fields = ("number",)
