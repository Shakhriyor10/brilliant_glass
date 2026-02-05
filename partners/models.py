from django.db import models

class Partner(models.Model):
    CLIENT = "client"
    SUPPLIER = "supplier"
    TYPE_CHOICES = [
        (CLIENT, "Клиент"),
        (SUPPLIER, "Поставщик"),
    ]

    partner_type = models.CharField("Тип партнера", max_length=20, choices=TYPE_CHOICES)
    name = models.CharField("Название", max_length=255)
    phone = models.CharField("Телефон", max_length=50, blank=True)
    address = models.CharField("Адрес", max_length=255, blank=True)
    note = models.TextField("Примечание", blank=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["partner_type", "name"]),
        ]
        verbose_name = "Партнер"
        verbose_name_plural = "Партнеры"

    def __str__(self):
        return f"{self.name} ({self.get_partner_type_display()})"
