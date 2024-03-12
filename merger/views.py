import os

from PyPDF2 import PdfMerger
from PyPDF2.errors import PdfReadError

from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order, PdfFile
from .serializers import OrderSerializer, PdfFileSerializer


@api_view(["GET", "POST"])
def order_list(request):
    if request.method == "GET":
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        user = request.user
        if user.is_authenticated:
            serializer = OrderSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            content = {"error": "Unauthorized"}
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
def order_detail(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        content = {"error": "order does not exist"}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
def order_files(request, order_id):
    if request.method == "GET":
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            content = {"error": "order does not exist"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        pdf_files = PdfFile.objects.filter(order=order)
        serializer = PdfFileSerializer(pdf_files, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            content = {"error": "order does not exist"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        if order.pdf_files.count() >= 5:
            content = {"error": "you have reached the max files allowed in on merge."}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        serializer = PdfFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order=order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def merge_order_files(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        content = {"error": "order does not exist"}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

    if order.is_completed:
        content = {
            "error": "this order has already been completed. Please make a new order."
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


@api_view(["POST"])
def order_delete(request, id):
    if request.method == "POST":
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            content = {"error": "order does not exist"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        order.delete()
        content = {"deleted": "successfully deleted."}
        return Response(content, status=status.HTTP_204_NO_CONTENT)
