from decimal import Decimal
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import Coalesce
from orders.models import Order, OrderItem
from .models import Expense, Payment


def revenue_for_period(start_date, end_date) -> Decimal:
    total_expression = ExpressionWrapper(F("sale_price") * F("quantity"), output_field=DecimalField())
    total = (
        OrderItem.objects.filter(order__date__range=(start_date, end_date))
        .aggregate(total=Coalesce(Sum(total_expression), Decimal("0")))
        .get("total")
    )
    return total


def payments_for_period(start_date, end_date) -> Decimal:
    total = (
        Payment.objects.filter(date__range=(start_date, end_date))
        .aggregate(total=Coalesce(Sum("amount"), Decimal("0")))
        .get("total")
    )
    return total


def expenses_for_period(start_date, end_date) -> Decimal:
    total = (
        Expense.objects.filter(date__range=(start_date, end_date))
        .aggregate(total=Coalesce(Sum("amount"), Decimal("0")))
        .get("total")
    )
    return total


def cost_of_goods_for_period(start_date, end_date) -> Decimal:
    total_cost = Decimal("0")
    for order in Order.objects.filter(date__range=(start_date, end_date)):
        total_cost += order.total_cost()
    return total_cost


def profit_for_period(start_date, end_date) -> Decimal:
    return revenue_for_period(start_date, end_date) - cost_of_goods_for_period(start_date, end_date) - expenses_for_period(
        start_date, end_date
    )


def top_clients(limit=5):
    total_expression = ExpressionWrapper(F("items__sale_price") * F("items__quantity"), output_field=DecimalField())
    data = (
        Order.objects.values("client__name")
        .annotate(total=Coalesce(Sum(total_expression), Decimal("0")))
        .order_by("-total")[:limit]
    )
    return list(data)
