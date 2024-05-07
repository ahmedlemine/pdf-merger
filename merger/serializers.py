import magic

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Order, PdfFile

User = get_user_model()


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
            "original_name"
        ]


    def create(self, validated_data):
        file = validated_data.get('file')
        file_name = file.name
        validated_data['original_name'] = file_name
        return super().create(validated_data)


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

        size_limit = settings.MAX_PDF_FILE_SIZE

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
            "name",
            "created_on",
            "is_merged",
            "download_url",
            "download_count",
            "user",
            "pdf_files",
        ]
        read_only_fields = [
            "id",
            "created_on",
            "is_merged",
            "download_url",
            "download_count",
            "user",
            "pdf_files",
        ]
