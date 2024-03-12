from django.contrib import admin

from .models import Order, PdfFile


class PdfFileInline(admin.TabularInline):
    model = PdfFile
    raw_id_fields = ["order"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "date_created",
        "is_completed",
        "is_downloaded"
    )

    inlines = [PdfFileInline]


admin.site.register(PdfFile)
