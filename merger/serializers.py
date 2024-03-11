from django.contrib.auth.models import User

from rest_framework import serializers
from .models import Order, PdfFile

class UserSerializer(serializers.ModelSerializer):    
    class Meta:
        model = User
        fields = ['id']


class PdfFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PdfFile
        fields = ["id", "order", "file", "is_merged"]


class OrderSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    user = UserSerializer(read_only=True)
    is_completed = serializers.BooleanField(default=False)

    def create(self, validated_data):
        return Order.objects.create(**validated_data)