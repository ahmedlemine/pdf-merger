from django.urls import path
from . import views

app_name = "merger"

urlpatterns = [
    path("orders/", views.order_list, name="order-list"),
    path("orders/<uuid:id>/", views.order_detail, name="order-detail"),
    path("orders/<uuid:id>/files/", views.order_files, name="order-files"),
    path("orders/<uuid:id>/merge/", views.merge_order_files, name="order-merge"),
    path(
        "orders/<uuid:id>/download/", views.downlaod_merged_pdf, name="order-download"
    ),
    path("orders/<uuid:id>/delete/", views.order_delete, name="order-delete"),
]
