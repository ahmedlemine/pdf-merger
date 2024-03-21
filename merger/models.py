import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    is_merged = models.BooleanField(default=False)
    download_url = models.CharField(max_length=250, blank=True, null=True)
    download_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return str(self.id)


class PdfFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="pdf_files")
    file = models.FileField(upload_to="pdf_uploads")
    date_uploaded = models.DateTimeField(auto_now=True, editable=False)
    is_merged = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return str(self.id)
