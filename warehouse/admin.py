from django.contrib import admin
from .models import GlassType, StockReceipt, StockSheet


class StockSheetInline(admin.TabularInline):
    model = StockSheet
    extra = 1


@admin.register(GlassType)
class GlassTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(StockReceipt)
class StockReceiptAdmin(admin.ModelAdmin):
    list_display = ("id", "supplier", "date", "doc_no")
    list_filter = ("date", "supplier")
    search_fields = ("doc_no", "supplier__name")
    inlines = [StockSheetInline]


@admin.register(StockSheet)
class StockSheetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "glass_type",
        "thickness_mm",
        "width_mm",
        "height_mm",
        "quantity",
        "purchase_price_per_sheet",
        "remaining_area_m2_per_sheet",
        "created_at",
    )
    list_filter = ("glass_type", "thickness_mm")
    search_fields = ("receipt__doc_no",)