from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import OrderForm, OrderItemForm
from .models import Order
from .services import allocate_stock_for_item, NotEnoughStock


def order_list(request):
    orders = Order.objects.select_related("client").all()
    return render(request, "orders/order_list.html", {"orders": orders})


def order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            return redirect("orders:detail", order_id=order.id)
    else:
        form = OrderForm()
    return render(request, "orders/order_form.html", {"form": form})


def order_detail(request, order_id: int):
    order = get_object_or_404(Order.objects.select_related("client"), id=order_id)
    items = order.items.select_related("glass_type").all()
    payments = order.payments.all()
    return render(
        request,
        "orders/order_detail.html",
        {"order": order, "items": items, "payments": payments},
    )


def order_item_create(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        form = OrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.order = order
            try:
                with transaction.atomic():
                    item.save()
                    allocate_stock_for_item(item)
            except NotEnoughStock as exc:
                form.add_error(None, str(exc))
            else:
                return redirect("orders:detail", order_id=order.id)
    else:
        form = OrderItemForm()
    return render(
        request,
        "orders/orderitem_form.html",
        {"form": form, "order": order},
    )
