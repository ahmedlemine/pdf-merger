from rest_framework import serializers
from .models import Order, PdfFile


class PdfFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PdfFile
        fields = ["id", "order", "file", "is_merged"]


class OrderSerializer(serializers.ModelSerializer):
    pdf_files = PdfFileSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = ["id", "user", "is_completed", "pdf_files"]
