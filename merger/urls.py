from django.urls import path
from . import views

app_name = "merger"

urlpatterns = [
    path("orders/", views.Orders.as_view(), name="order-list"),
    path("orders/<uuid:pk>/", views.OrderDetail.as_view(), name="order-detail"),
    path("orders/<uuid:pk>/files/", views.OrderFilesList.as_view(), name="order-files"),
    path(
        "orders/<uuid:pk>/add_files/",
        views.OrderFilesCreate.as_view(),
        name="order-files-create",
    ),
    path("orders/<uuid:id>/merge/", views.merge_order_files, name="order-merge"),
    path(
        "orders/<uuid:id>/download/", views.downlaod_merged_pdf, name="order-download"
    ),
    path("files/<uuid:pk>/delete/", views.FileDelete.as_view(), name="files-delete"),
]
