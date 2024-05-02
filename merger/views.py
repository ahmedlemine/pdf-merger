from datetime import datetime, timedelta

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.reverse import reverse_lazy


from .utils import merge_pdf_files
from .permissions import IsOwner, IsParentOwner
from .models import Order, PdfFile
from .serializers import OrderSerializer, PdfFileSerializer


class APIRootView(APIView):
    def get(self, request):
        data = {
            "orders": reverse_lazy("merger:order-list", request=request),
        }
        return Response(data)


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

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = PdfFileSerializer

    def get_queryset(self):
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, order)
        user = self.request.user
        return PdfFile.objects.filter(order=order, order__user=user)


class OrderFilesCreate(GenericAPIView, CreateModelMixin):
    """Create (add) files for the order specified by its id"""

    permission_classes = [IsAuthenticated]
    serializer_class = PdfFileSerializer

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs["pk"])
        user = self.request.user
        if order.user != user:
            raise PermissionDenied

        if order.pdf_files.count() >= settings.MAX_MERGED_FILES_LIMIT:
            content = {"error": "you have reached the max files allowed in one merge."}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if order.is_merged:
            content = {
                "error": "Merge has already been merged and archived. Please create a new order."
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

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


class OrderMerge(APIView):
    """Merge PDF files of an order"""

    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        obj = order
        self.check_object_permissions(self.request, obj)

        if order.is_merged:
            content = {
                "error": "This order has already been merged. Download merged PDF or make a new order."
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        pdf_files = PdfFile.objects.filter(order=order)

        if pdf_files.count() < 2:
            content = {
                "error": "Not enough PDFs to merge. Please make sure you have added at least 2 PDF files to merge."
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        merged_path = merge_pdf_files(pdf_files)

        if merged_path is not None:
            for f in pdf_files:
                f.is_merged = True
                f.save()

            order.is_merged = True
            order.download_url = merged_path
            order.save()

            content = {
                "download_url": merged_path
            }
            return Response(content, status=status.HTTP_201_CREATED)

        content = {"error": "Error merging PDF files"}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


class OrderDownload(APIView):
    """Returns download link of an already merged order"""

    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        obj = order
        self.check_object_permissions(self.request, obj)

        time_delta = timezone.now().date() - order.created_on.date()
        time_since = time_delta.total_seconds() / (60 * 60)

        if time_since > settings.MAX_TIME_ALLOWED_FOR_DOWNLOAD:
            content = {
                "error": "Order reached allowed time on server and is set to be deleted. Please create a new order."
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if not order.is_merged:
            content = {"error": "order has not been merged yet."}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if order.download_count >= settings.MAX_ORDER_DOWNLOADS:
            content = {
                "error": "Order reached maximum allowed downloads and is set to be deleted. Please create a new order."
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        order.download_count += 1
        order.save()

        content = {"download_url": order.download_url}
        return Response(content, status=status.HTTP_200_OK)
