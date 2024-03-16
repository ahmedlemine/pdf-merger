from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin


from .utils import merge_pdf_files
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

        if order.is_completed:
            content = {
                "error": "merge has already been completed and archived. Please create a new order."
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

        if order.is_completed:
            content = {
                "error": "this order has already been merged. Download merged PDF or make a new order."
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        pdf_files = PdfFile.objects.filter(order=order)

        if pdf_files.count() < 2:
            content = {
                "error": "not enough PDFs to merge. Please make sure you have added at least 2 PDF files to merge."
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        merged_path = merge_pdf_files(pdf_files)

        if merged_path is not None:
            for f in pdf_files:
                f.is_merged = True
                f.save()

            order.is_completed = True
            order.download_url = merged_path
            order.save()

            content = {
                "success": "files merged successfully. Use download link to download the merged PDF file."
            }
            return Response(content, status=status.HTTP_201_CREATED)

        content = {"error": "error merging PDF files"}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


class OrderDownload(APIView):
    """Returns download link of an already merged order"""

    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        obj = order
        self.check_object_permissions(self.request, obj)

        if not order.is_completed:
            content = {"error": "order has not been merged yet."}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if order.is_archived:
            content = {
                "error": "order has already been downloaded and archived. Please create a new order."
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        order.is_archived = True
        order.save()

        content = {"download_url": order.download_url}
        return Response(content, status=status.HTTP_200_OK)
