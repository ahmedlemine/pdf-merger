from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order, PdfFile
from .serializers import OrderSerializer, PdfFileSerializer

from django.shortcuts import get_object_or_404

@api_view(["get", "post"])
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


@api_view(["get"])
def order_detail(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        content = {"error": "order does not exist"}
        return Response(content, status=status.HTTP_404_NOT_FOUND)
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["get", "post"])
def pdf_file_list(request, order_id):
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
            serializer = PdfFileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(order=order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            content = {"error": "order does not exist"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)