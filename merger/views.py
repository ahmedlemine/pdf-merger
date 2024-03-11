from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order, PdfFile
from .serializers import OrderSerializer, PdfFileSerializer


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


@api_view(["get", "post"])
def pdf_file_list(request):
    if request.method == "GET":
        pdf_files = PdfFile.objects.all()
        serializer = PdfFileSerializer(pdf_files, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = PdfFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
