import magic

from django.contrib.auth.models import User

from rest_framework import serializers
from .models import Order, PdfFile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id"]


class OrderSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    date_created = serializers.DateTimeField(read_only=True)
    is_completed = serializers.BooleanField(default=False, read_only=True)
    download_url = serializers.URLField(read_only=True)
    is_downloaded = serializers.BooleanField(default=False, read_only=True)
    user = UserSerializer(read_only=True)
    pdf_files = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def create(self, validated_data):
        return Order.objects.create(**validated_data)


class PdfFileSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    order = OrderSerializer(read_only=True)
    file = serializers.FileField()
    is_merged = serializers.BooleanField(default=False)
    date_uploaded = serializers.DateTimeField(read_only=True)

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

        # limit file upload size to 2mb
        size_limit = 2097152

        if file.size > size_limit:
            raise serializers.ValidationError(
                f"error: '{file.name}' file exeeds size limit."
            )
        return file

    def create(self, validated_data):
        return PdfFile.objects.create(**validated_data)
