from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from partners.models import Partner

class GlassType(models.Model):
    name = models.CharField(max_length=120, unique=True)  # Прозрачное, Зеркало, Тонированное
    def __str__(self):
        return self.name

class StockReceipt(models.Model):
    supplier = models.ForeignKey(
        Partner,
        on_delete=models.PROTECT,
        limit_choices_to={"partner_type": Partner.SUPPLIER},
        related_name="receipts"
    )
    doc_no = models.CharField(max_length=80, blank=True)
    date = models.DateField()
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt #{self.id} from {self.supplier.name}"

class StockSheet(models.Model):
    """
    Лист стекла (или партия листов одного размера).
    Мы храним остаток по площади.
    """
    receipt = models.ForeignKey(StockReceipt, on_delete=models.CASCADE, related_name="sheets")

    glass_type = models.ForeignKey(GlassType, on_delete=models.PROTECT)
    thickness_mm = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    width_mm = models.PositiveIntegerField()
    height_mm = models.PositiveIntegerField()

    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    purchase_price_per_sheet = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])

    # Остаток по площади (на 1 лист) в м2 — удобно считать списания
    remaining_area_m2_per_sheet = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def sheet_area_m2(self) -> Decimal:
        return (Decimal(self.width_mm) * Decimal(self.height_mm)) / Decimal(1_000_000)

    def total_remaining_area_m2(self) -> Decimal:
        return Decimal(self.remaining_area_m2_per_sheet) * Decimal(self.quantity)

    def save(self, *args, **kwargs):
        # при создании: остаток = полная площадь листа
        if self.remaining_area_m2_per_sheet == 0:
            self.remaining_area_m2_per_sheet = self.sheet_area_m2()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.glass_type} {self.thickness_mm}mm {self.width_mm}x{self.height_mm} qty={self.quantity}"
