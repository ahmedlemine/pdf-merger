from django.urls import path
from . import views

app_name = "merger"

urlpatterns = [
    path("", views.order_list, name="order-list"),
    path("files", views.pdf_file_list, name="file-list"),
]
