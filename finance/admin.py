from django.contrib import admin
from .models import Expense, ExpenseCategory, Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "amount", "method", "date")
    list_filter = ("method", "date")
    search_fields = ("order__client__name",)


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "amount", "date")
    list_filter = ("category", "date")
    search_fields = ("category__name",)