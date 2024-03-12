from django.urls import path
from . import views

app_name = "merger"

urlpatterns = [
    path("orders/", views.order_list, name="order-list"),
    path("orders/<uuid:id>/", views.order_detail, name="order-detail"),
    path("orders/files/<uuid:order_id>/", views.order_files, name="order-files"),
    path("orders/merge/<uuid:id>/", views.merge_order_files, name="order-merge"),
]
