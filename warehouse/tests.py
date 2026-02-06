from datetime import date
from django.test import TestCase
from django.urls import reverse

from partners.models import Partner
from warehouse.models import GlassType, StockReceipt, StockSheet


class WarehouseFlowTests(TestCase):
    def setUp(self):
        self.supplier = Partner.objects.create(partner_type=Partner.SUPPLIER, name="Supplier 1")
        self.glass_type = GlassType.objects.create(name="Clear")

    def test_stock_income_create_creates_receipt_and_sheet(self):
        response = self.client.post(
            reverse("warehouse:stock_income_create"),
            data={
                "supplier": self.supplier.id,
                "date": "2026-01-01",
                "doc_no": "A-1",
                "note": "test",
                "glass_type": self.glass_type.id,
                "thickness_mm": 4,
                "width_mm": 2000,
                "height_mm": 3000,
                "quantity": 2,
                "purchase_price_per_sheet": "100.00",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(StockReceipt.objects.count(), 1)
        self.assertEqual(StockSheet.objects.count(), 1)
        sheet = StockSheet.objects.get()
        self.assertEqual(float(sheet.sheet_area_m2()), 6.0)
        self.assertEqual(float(sheet.total_remaining_area_m2()), 12.0)

    def test_stock_sheet_list_contains_summary(self):
        receipt = StockReceipt.objects.create(supplier=self.supplier, date=date(2026, 1, 1))
        StockSheet.objects.create(
            receipt=receipt,
            glass_type=self.glass_type,
            thickness_mm=4,
            width_mm=1000,
            height_mm=2000,
            quantity=3,
            purchase_price_per_sheet="50.00",
        )

        response = self.client.get(reverse("warehouse:stock_sheet_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Листов на складе")
        self.assertContains(response, "Clear")
