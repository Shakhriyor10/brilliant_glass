from datetime import date
from decimal import Decimal
from django.test import TestCase
from partners.models import Partner
from warehouse.models import GlassType, StockReceipt, StockSheet
from .models import Order, OrderItem, StockConsumption
from .services import NotEnoughStock, allocate_stock_for_item
from finance.models import Payment


class StockAllocationTests(TestCase):
    def setUp(self):
        self.supplier = Partner.objects.create(partner_type=Partner.SUPPLIER, name="Supplier")
        self.client = Partner.objects.create(partner_type=Partner.CLIENT, name="Client")
        self.glass_type = GlassType.objects.create(name="Clear")
        self.receipt = StockReceipt.objects.create(supplier=self.supplier, date=date.today())

    def test_successful_allocation(self):
        sheet = StockSheet.objects.create(
            receipt=self.receipt,
            glass_type=self.glass_type,
            thickness_mm=4,
            width_mm=1000,
            height_mm=1000,
            quantity=1,
            purchase_price_per_sheet=Decimal("100.00"),
        )
        order = Order.objects.create(client=self.client, status=Order.NEW, date=date.today())
        item = OrderItem.objects.create(
            order=order,
            glass_type=self.glass_type,
            thickness_mm=4,
            width_mm=500,
            height_mm=500,
            quantity=2,
            sale_price=Decimal("200.00"),
        )

        allocate_stock_for_item(item)

        sheet.refresh_from_db()
        self.assertEqual(StockConsumption.objects.count(), 1)
        self.assertEqual(sheet.remaining_area_m2_per_sheet, Decimal("0.5000"))

    def test_not_enough_stock(self):
        StockSheet.objects.create(
            receipt=self.receipt,
            glass_type=self.glass_type,
            thickness_mm=4,
            width_mm=1000,
            height_mm=1000,
            quantity=1,
            purchase_price_per_sheet=Decimal("100.00"),
        )
        order = Order.objects.create(client=self.client, status=Order.NEW, date=date.today())
        item = OrderItem.objects.create(
            order=order,
            glass_type=self.glass_type,
            thickness_mm=4,
            width_mm=1000,
            height_mm=1000,
            quantity=2,
            sale_price=Decimal("200.00"),
        )

        with self.assertRaises(NotEnoughStock):
            allocate_stock_for_item(item)

        self.assertEqual(StockConsumption.objects.count(), 0)

    def test_cost_calculation(self):
        StockSheet.objects.create(
            receipt=self.receipt,
            glass_type=self.glass_type,
            thickness_mm=4,
            width_mm=1000,
            height_mm=1000,
            quantity=1,
            purchase_price_per_sheet=Decimal("100.00"),
        )
        order = Order.objects.create(client=self.client, status=Order.NEW, date=date.today())
        item = OrderItem.objects.create(
            order=order,
            glass_type=self.glass_type,
            thickness_mm=4,
            width_mm=500,
            height_mm=500,
            quantity=2,
            sale_price=Decimal("200.00"),
        )

        allocate_stock_for_item(item)

        self.assertEqual(order.total_cost(), Decimal("50.0000"))


class OrderDebtTests(TestCase):
    def test_debt_calculation(self):
        client = Partner.objects.create(partner_type=Partner.CLIENT, name="Debt Client")
        glass_type = GlassType.objects.create(name="Mirror")
        order = Order.objects.create(client=client, status=Order.NEW, date=date.today())
        OrderItem.objects.create(
            order=order,
            glass_type=glass_type,
            thickness_mm=4,
            width_mm=1000,
            height_mm=1000,
            quantity=1,
            sale_price=Decimal("500.00"),
        )
        Payment.objects.create(order=order, amount=Decimal("200.00"), method=Payment.CASH, date=date.today())

        self.assertEqual(order.debt(), Decimal("300.00"))
