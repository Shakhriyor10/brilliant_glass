from django.core.validators import MinValueValidator
from django.db import models
from orders.models import Order


class Payment(models.Model):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    METHOD_CHOICES = [
        (CASH, "Наличные"),
        (CARD, "Карта"),
        (TRANSFER, "Перевод"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments", verbose_name="Заказ")
    amount = models.DecimalField("Сумма", max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    method = models.CharField("Способ оплаты", max_length=20, choices=METHOD_CHOICES)
    date = models.DateField("Дата")
    note = models.TextField("Примечание", blank=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Платеж №{self.id} по заказу №{self.order_id}"


class ExpenseCategory(models.Model):
    name = models.CharField("Название", max_length=120, unique=True)

    class Meta:
        verbose_name = "Категория расходов"
        verbose_name_plural = "Категории расходов"

    def __str__(self):
        return self.name


class Expense(models.Model):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name="expenses", verbose_name="Категория")
    amount = models.DecimalField("Сумма", max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    date = models.DateField("Дата")
    note = models.TextField("Примечание", blank=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"

    def __str__(self):
        return f"Расход №{self.id} {self.category.name}"
