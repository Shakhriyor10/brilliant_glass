from django.shortcuts import render, redirect, get_object_or_404
from .forms import PaymentForm, ExpenseCategoryForm, ExpenseForm
from .models import ExpenseCategory, Expense
from orders.models import Order


def payment_create(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order
            payment.save()
            return redirect("orders:detail", order_id=order.id)
    else:
        form = PaymentForm()
    return render(request, "finance/payment_form.html", {"form": form, "order": order})


def expense_category_list(request):
    categories = ExpenseCategory.objects.all().order_by("name")
    return render(request, "finance/expense_category_list.html", {"categories": categories})


def expense_category_create(request):
    if request.method == "POST":
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("finance:expense_category_list")
    else:
        form = ExpenseCategoryForm()
    return render(request, "finance/expense_category_form.html", {"form": form})


def expense_list(request):
    expenses = Expense.objects.select_related("category").all()
    return render(request, "finance/expense_list.html", {"expenses": expenses})


def expense_create(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("finance:expense_list")
    else:
        form = ExpenseForm()
    return render(request, "finance/expense_form.html", {"form": form})
