from django.urls import path
from . import views

app_name = "merger"

urlpatterns = [
    path("orders/", views.order_list, name="order-list"),
    path("order/<uuid:id>/", views.order_detail, name="order-detail"),
    path("files/<uuid:order_id>/", views.pdf_file_list, name="file-list"),
    
    
]
