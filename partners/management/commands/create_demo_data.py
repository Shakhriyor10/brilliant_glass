from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from finance.models import Expense, ExpenseCategory, Payment
from orders.models import Order, OrderItem
from partners.models import Partner
from warehouse.models import GlassType, StockReceipt, StockSheet


class Command(BaseCommand):
    help = "Create demo data for suppliers, clients, receipts, orders, payments, and expenses."

    def handle(self, *args, **options):
        supplier, _ = Partner.objects.get_or_create(partner_type=Partner.SUPPLIER, name="Glass Supplier")
        client_a, _ = Partner.objects.get_or_create(partner_type=Partner.CLIENT, name="Client A")
        client_b, _ = Partner.objects.get_or_create(partner_type=Partner.CLIENT, name="Client B")

        clear, _ = GlassType.objects.get_or_create(name="Clear")
        mirror, _ = GlassType.objects.get_or_create(name="Mirror")

        receipt = StockReceipt.objects.create(supplier=supplier, date=date.today())
        StockSheet.objects.create(
            receipt=receipt,
            glass_type=clear,
            thickness_mm=4,
            width_mm=1000,
            height_mm=2000,
            quantity=10,
            purchase_price_per_sheet=Decimal("120.00"),
        )
        StockSheet.objects.create(
            receipt=receipt,
            glass_type=mirror,
            thickness_mm=5,
            width_mm=1200,
            height_mm=2000,
            quantity=5,
            purchase_price_per_sheet=Decimal("200.00"),
        )

        order1 = Order.objects.create(client=client_a, status=Order.NEW, date=date.today())
        OrderItem.objects.create(
            order=order1,
            glass_type=clear,
            thickness_mm=4,
            width_mm=500,
            height_mm=500,
            quantity=4,
            sale_price=Decimal("150.00"),
        )
        OrderItem.objects.create(
            order=order1,
            glass_type=mirror,
            thickness_mm=5,
            width_mm=600,
            height_mm=800,
            quantity=2,
            sale_price=Decimal("250.00"),
        )

        order2 = Order.objects.create(client=client_b, status=Order.NEW, date=date.today() - timedelta(days=2))
        OrderItem.objects.create(
            order=order2,
            glass_type=clear,
            thickness_mm=4,
            width_mm=1000,
            height_mm=1000,
            quantity=1,
            sale_price=Decimal("220.00"),
        )

        Payment.objects.create(order=order1, amount=Decimal("200.00"), method=Payment.CARD, date=date.today())
        Payment.objects.create(order=order2, amount=Decimal("100.00"), method=Payment.CASH, date=date.today())

        salary, _ = ExpenseCategory.objects.get_or_create(name="Salary")
        rent, _ = ExpenseCategory.objects.get_or_create(name="Rent")
        Expense.objects.create(category=salary, amount=Decimal("500.00"), date=date.today(), note="Monthly salary")
        Expense.objects.create(category=rent, amount=Decimal("300.00"), date=date.today(), note="Office rent")

        self.stdout.write(self.style.SUCCESS("Demo data created."))
