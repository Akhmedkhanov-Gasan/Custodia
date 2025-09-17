from rest_framework import serializers
from .models import Good, Order

class GoodSerializer(serializers.ModelSerializer):
    owner = serializers.IntegerField(source="owner_id", read_only=True)

    class Meta:
        model = Good
        fields = ["id", "title", "owner", "created_at", "updated_at"]

class OrderSerializer(serializers.ModelSerializer):
    owner = serializers.IntegerField(source="owner_id", read_only=True)

    class Meta:
        model = Order
        fields = ["id", "number", "owner", "created_at", "updated_at"]
