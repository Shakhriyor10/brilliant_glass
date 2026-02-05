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
        (NEW, "Новый"),
        (IN_WORK, "В работе"),
        (CUTTING, "Резка"),
        (READY, "Готов"),
        (DELIVERED, "Доставлен"),
        (CANCELED, "Отменен"),
    ]

    client = models.ForeignKey(
        Partner,
        on_delete=models.PROTECT,
        limit_choices_to={"partner_type": Partner.CLIENT},
        related_name="orders",
        verbose_name="Клиент"
    )
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default=NEW)
    date = models.DateField("Дата")
    note = models.TextField("Примечание", blank=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def total_amount(self) -> Decimal:
        return sum((item.total_sum() for item in self.items.all()), Decimal("0"))

    def total_paid(self) -> Decimal:
        return sum((payment.amount for payment in self.payments.all()), Decimal("0"))

    def total_cost(self) -> Decimal:
        return sum((item.total_cost() for item in self.items.all()), Decimal("0"))

    def debt(self) -> Decimal:
        return self.total_amount() - self.total_paid()

    def __str__(self):
        return f"Заказ №{self.id} ({self.client.name})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")

    glass_type = models.ForeignKey(GlassType, on_delete=models.PROTECT, verbose_name="Вид стекла")
    thickness_mm = models.PositiveIntegerField("Толщина, мм", validators=[MinValueValidator(1)])

    width_mm = models.PositiveIntegerField("Ширина, мм")
    height_mm = models.PositiveIntegerField("Высота, мм")
    quantity = models.PositiveIntegerField("Количество", default=1, validators=[MinValueValidator(1)])

    sale_price = models.DecimalField("Цена продажи", max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])

    def area_m2_one(self) -> Decimal:
        return (Decimal(self.width_mm) * Decimal(self.height_mm)) / Decimal(1_000_000)

    def area_m2_total(self) -> Decimal:
        return self.area_m2_one() * Decimal(self.quantity)

    def total_sum(self) -> Decimal:
        return Decimal(self.sale_price) * Decimal(self.quantity)

    def total_cost(self) -> Decimal:
        return sum((consumption.cost_amount() for consumption in self.consumptions.all()), Decimal("0"))

    def __str__(self):
        return f"Позиция №{self.id} для заказа №{self.order_id}"

class StockConsumption(models.Model):
    """
    Списание со склада под конкретную позицию заказа.
    """
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="consumptions", verbose_name="Позиция заказа")
    stock_sheet = models.ForeignKey(StockSheet, on_delete=models.PROTECT, related_name="consumptions", verbose_name="Складской лист")

    consumed_area_m2 = models.DecimalField("Площадь списания, м²", max_digits=14, decimal_places=4, validators=[MinValueValidator(0)])

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        verbose_name = "Списание со склада"
        verbose_name_plural = "Списания со склада"

    def cost_amount(self) -> Decimal:
        return Decimal(self.consumed_area_m2) * self.stock_sheet.cost_per_m2()

    def __str__(self):
        return f"Списание {self.consumed_area_m2} м2 с листа {self.stock_sheet_id}"
