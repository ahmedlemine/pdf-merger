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
    path("orders/<uuid:pk>/merge/", views.OrderMerge.as_view(), name="order-merge"),
    path(
        "orders/<uuid:pk>/download/",
        views.OrderDownload.as_view(),
        name="order-download",
    ),
    path("files/<uuid:pk>/delete/", views.FileDelete.as_view(), name="files-delete"),
]
