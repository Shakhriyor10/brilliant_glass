from django.contrib import admin, messages
from .models import Order, OrderItem, StockConsumption
from .services import NotEnoughStock, allocate_stock_for_order


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.action(description="Списать стекло со склада")
def allocate_stock_action(modeladmin, request, queryset):
    for order in queryset:
        try:
            allocate_stock_for_order(order)
            order.status = Order.IN_WORK
            order.save(update_fields=["status"])
        except NotEnoughStock as exc:
            messages.error(request, str(exc))


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "status", "date", "total_amount", "total_paid", "debt")
    list_filter = ("status", "date")
    search_fields = ("client__name",)
    inlines = [OrderItemInline]
    actions = [allocate_stock_action]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "glass_type", "thickness_mm", "width_mm", "height_mm", "quantity", "sale_price")
    list_filter = ("glass_type", "thickness_mm")
    search_fields = ("order__client__name",)


@admin.register(StockConsumption)
class StockConsumptionAdmin(admin.ModelAdmin):
    list_display = ("id", "order_item", "stock_sheet", "consumed_area_m2", "created_at")
    list_filter = ("stock_sheet__glass_type", "stock_sheet__thickness_mm")
