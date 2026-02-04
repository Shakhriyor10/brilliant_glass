from django.db import models

class Partner(models.Model):
    CLIENT = "client"
    SUPPLIER = "supplier"
    TYPE_CHOICES = [
        (CLIENT, "Client"),
        (SUPPLIER, "Supplier"),
    ]

    partner_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["partner_type", "name"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.partner_type})"
