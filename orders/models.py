from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from partners.models import Partner
from warehouse.models import GlassType, StockSheet

class Order(models.Model):
    NEW = "new"
    IN_WORK = "in_work"
    CUTTING = "cutting"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELED = "canceled"

    STATUS_CHOICES = [
        (NEW, "New"),
        (IN_WORK, "In work"),
        (CUTTING, "Cutting"),
        (READY, "Ready"),
        (DELIVERED, "Delivered"),
        (CANCELED, "Canceled"),
    ]

    client = models.ForeignKey(
        Partner,
        on_delete=models.PROTECT,
        limit_choices_to={"partner_type": Partner.CLIENT},
        related_name="orders"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NEW)
    date = models.DateField()
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def total_amount(self) -> Decimal:
        return sum((item.total_sum() for item in self.items.all()), Decimal("0"))

    def total_paid(self) -> Decimal:
        return sum((payment.amount for payment in self.payments.all()), Decimal("0"))

    def total_cost(self) -> Decimal:
        return sum((item.total_cost() for item in self.items.all()), Decimal("0"))

    def debt(self) -> Decimal:
        return self.total_amount() - self.total_paid()

    def __str__(self):
        return f"Order #{self.id} ({self.client.name})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    glass_type = models.ForeignKey(GlassType, on_delete=models.PROTECT)
    thickness_mm = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    width_mm = models.PositiveIntegerField()
    height_mm = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    sale_price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])

    def area_m2_one(self) -> Decimal:
        return (Decimal(self.width_mm) * Decimal(self.height_mm)) / Decimal(1_000_000)

    def area_m2_total(self) -> Decimal:
        return self.area_m2_one() * Decimal(self.quantity)

    def total_sum(self) -> Decimal:
        return Decimal(self.sale_price) * Decimal(self.quantity)

    def total_cost(self) -> Decimal:
        return sum((consumption.cost_amount() for consumption in self.consumptions.all()), Decimal("0"))

    def __str__(self):
        return f"Item #{self.id} for Order #{self.order_id}"

class StockConsumption(models.Model):
    """
    Списание со склада под конкретную позицию заказа.
    """
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="consumptions")
    stock_sheet = models.ForeignKey(StockSheet, on_delete=models.PROTECT, related_name="consumptions")

    consumed_area_m2 = models.DecimalField(max_digits=14, decimal_places=4, validators=[MinValueValidator(0)])

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def cost_amount(self) -> Decimal:
        return Decimal(self.consumed_area_m2) * self.stock_sheet.cost_per_m2()

    def __str__(self):
        return f"Consume {self.consumed_area_m2} m2 from sheet {self.stock_sheet_id}"