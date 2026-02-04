from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("orders/<int:order_id>/payments/new/", views.payment_create, name="payment_create"),
    path("expense-categories/", views.expense_category_list, name="expense_category_list"),
    path("expense-categories/new/", views.expense_category_create, name="expense_category_create"),
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/new/", views.expense_create, name="expense_create"),
]
