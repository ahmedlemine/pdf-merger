import magic

from django.contrib.auth.models import User

from rest_framework import serializers
from .models import Order, PdfFile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id"]


class PdfFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PdfFile
        fields = "__all__"
        read_only_fields = [
            "id",
            "order",
            "is_merged",
            "date_uploaded",
        ]

    def validate_file(self, file):
        if file.content_type != "application/pdf":
            raise serializers.ValidationError(
                f"error: '{file.name}' is not a PDF file. Please make sure to upload only PDF files."
            )

        mimetype = magic.from_buffer(file.read(2048), mime=True)
        if mimetype != "application/pdf":
            raise serializers.ValidationError(
                f"error: '{file.name}' is not a PDF file. Please make sure to upload only PDF files."
            )

        size_limit = 2097152

        if file.size > size_limit:
            raise serializers.ValidationError(
                f"error: '{file.name}' file exeeds size limit."
            )
        return file


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    pdf_files = PdfFileSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        depth = 1
        fields = [
            "id",
            "date_created",
            "is_completed",
            "download_url",
            "is_downloaded",
            "is_archived",
            "user",
            "pdf_files",
        ]
        read_only_fields = [
            "id",
            "date_created",
            "is_completed",
            "download_url",
            "is_downloaded",
            "is_archived",
            "user",
            "pdf_files",
        ]
