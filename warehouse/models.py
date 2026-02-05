from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from partners.models import Partner

class GlassType(models.Model):
    name = models.CharField("Название", max_length=120, unique=True)  # Прозрачное, Зеркало, Тонированное

    class Meta:
        verbose_name = "Вид стекла"
        verbose_name_plural = "Виды стекла"

    def __str__(self):
        return self.name

class StockReceipt(models.Model):
    supplier = models.ForeignKey(
        Partner,
        on_delete=models.PROTECT,
        limit_choices_to={"partner_type": Partner.SUPPLIER},
        related_name="receipts",
        verbose_name="Поставщик"
    )
    doc_no = models.CharField("Номер документа", max_length=80, blank=True)
    date = models.DateField("Дата")
    note = models.TextField("Примечание", blank=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Приход"
        verbose_name_plural = "Приходы"

    def __str__(self):
        return f"Приход №{self.id} от {self.supplier.name}"

class StockSheet(models.Model):
    """
    Лист стекла (или партия листов одного размера).
    Мы храним остаток по площади.
    """
    receipt = models.ForeignKey(StockReceipt, on_delete=models.CASCADE, related_name="sheets", verbose_name="Приход")

    glass_type = models.ForeignKey(GlassType, on_delete=models.PROTECT, verbose_name="Вид стекла")
    thickness_mm = models.PositiveIntegerField("Толщина, мм", validators=[MinValueValidator(1)])

    width_mm = models.PositiveIntegerField("Ширина, мм")
    height_mm = models.PositiveIntegerField("Высота, мм")

    quantity = models.PositiveIntegerField("Количество", default=1, validators=[MinValueValidator(1)])
    purchase_price_per_sheet = models.DecimalField("Цена закупки за лист", max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])

    # Остаток по площади (на 1 лист) в м2 — удобно считать списания
    remaining_area_m2_per_sheet = models.DecimalField("Остаток м² на лист", max_digits=14, decimal_places=4, default=0)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        verbose_name = "Складской лист"
        verbose_name_plural = "Складские листы"

    def sheet_area_m2(self) -> Decimal:
        return (Decimal(self.width_mm) * Decimal(self.height_mm)) / Decimal(1_000_000)

    def cost_per_m2(self) -> Decimal:
        area = self.sheet_area_m2()
        if area == 0:
            return Decimal("0")
        return Decimal(self.purchase_price_per_sheet) / area

    def total_remaining_area_m2(self) -> Decimal:
        return Decimal(self.remaining_area_m2_per_sheet) * Decimal(self.quantity)

    def save(self, *args, **kwargs):
        # при создании: остаток = полная площадь листа
        if self.remaining_area_m2_per_sheet == 0:
            self.remaining_area_m2_per_sheet = self.sheet_area_m2()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.glass_type} {self.thickness_mm}мм {self.width_mm}x{self.height_mm} шт={self.quantity}"
