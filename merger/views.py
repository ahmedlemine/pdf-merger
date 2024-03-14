import os

from PyPDF2 import PdfMerger
from PyPDF2.errors import PdfReadError

from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin


from .permissions import IsOwner, IsParentOwner
from .models import Order, PdfFile
from .serializers import OrderSerializer, PdfFileSerializer


class Orders(generics.ListCreateAPIView):
    """List orders that belong to the currently authenticated user, and create new orders for the user"""

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        return serializer.save(user=user)


class OrderDetail(generics.RetrieveDestroyAPIView):
    """Show details of an order by its id"""

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


class OrderFilesList(generics.ListAPIView):
    """List all files under order that belongs to the currently authenticated user"""

    permission_classes = [IsAuthenticated]
    serializer_class = PdfFileSerializer

    def get_queryset(self):
        user = self.request.user
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        if order.user != user:
            raise PermissionDenied
        return PdfFile.objects.filter(order=order, order__user=user)


class OrderFilesCreate(GenericAPIView, CreateModelMixin):
    """Create (add) files for the order specified by its id"""

    permission_classes = [IsAuthenticated]
    serializer_class = PdfFileSerializer

    def create(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs["pk"])

        if order.pdf_files.count() >= settings.MAX_MERGED_FILES_LIMIT:
            content = {"error": "you have reached the max files allowed in on merge."}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if order.is_completed:
            content = {
                "error": "merge has already been completed and archived. Please create a new order"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        headers = self.get_success_headers(serializer.data)
        super().create(self, request, *args, **kwargs)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        order = get_object_or_404(Order, id=self.kwargs["pk"])
        return serializer.save(order=order)


class FileDelete(generics.DestroyAPIView):
    """Delete file by its id"""

    permission_classes = [IsAuthenticated, IsParentOwner]
    serializer_class = PdfFileSerializer
    queryset = PdfFile.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


@api_view(["GET"])
def merge_order_files(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        content = {"error": "order does not exist"}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

    if order.is_completed:
        content = {
            "error": "this order has already been completed. Download merged PDF or make a new order."
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    pdf_files = PdfFile.objects.filter(order=order)

    if pdf_files.count() < 2:
        content = {
            "error": "not enough PDFs to merge. Please make sure you have added at least 2 PDF files."
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    merger = PdfMerger()
    for f in pdf_files:
        merger.append(f.file)

    output_name = os.path.join(
        settings.MEDIA_ROOT, f"merged_pdfs/merged_pdf_{order.id}.pdf"
    )

    try:
        merger.write(output_name)
    except PdfReadError:
        content = {"error": "error reading PDF file"}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    merger.close()

    for f in pdf_files:
        f.is_merged = True
        f.save()

    order.is_completed = True
    order.download_url = output_name
    order.save()

    content = {
        "success": "files merged successfully. Use download link to download the merged PDF file"
    }
    return Response(content, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def downlaod_merged_pdf(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        content = {"error": "order does not exist"}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

    if not order.is_completed:
        content = {"error": "order has not been merged yet"}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if order.is_archived:
        content = {
            "error": "order has already been downloaded and archived. Please create a new order"
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    order.is_archived = True
    order.save()

    content = {"download_url": order.download_url}
    return Response(content, status=status.HTTP_200_OK)
