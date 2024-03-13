from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("api/v1/", include("merger.urls", namespace="merger")),
    path("admin/", admin.site.urls),
]
