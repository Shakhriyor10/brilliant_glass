from django.contrib import admin
from .models import Partner


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "partner_type", "phone", "address", "created_at")
    list_filter = ("partner_type",)
    search_fields = ("name", "phone", "address")