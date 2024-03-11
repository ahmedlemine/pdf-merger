from django.contrib.auth.models import User

from rest_framework import serializers
from .models import Order, PdfFile

class UserSerializer(serializers.ModelSerializer):    
    class Meta:
        model = User
        fields = ['id']


class OrderSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    date_created = serializers.DateTimeField(read_only=True)
    is_completed = serializers.BooleanField(default=False)
    user = UserSerializer(read_only=True)
    pdf_files = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True)

    def create(self, validated_data):
        return Order.objects.create(**validated_data) 

class PdfFileSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    order = OrderSerializer(read_only=True)
    file = serializers.FileField()
    is_merged = serializers.BooleanField(default=False)

    def create(self, validated_data):
        return PdfFile.objects.create(**validated_data)
