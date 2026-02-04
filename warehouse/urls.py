from django.urls import path
from . import views

app_name = "warehouse"

urlpatterns = [
    path("glass-types/", views.glass_type_list, name="glass_type_list"),
    path("glass-types/new/", views.glass_type_create, name="glass_type_create"),
    path("receipts/", views.stock_receipt_list, name="stock_receipt_list"),
    path("receipts/new/", views.stock_receipt_create, name="stock_receipt_create"),
    path("sheets/", views.stock_sheet_list, name="stock_sheet_list"),
    path("sheets/new/", views.stock_sheet_create, name="stock_sheet_create"),
]
