from django import forms
from .models import GlassType, StockReceipt, StockSheet


class FormControlMixin:
    def apply_bootstrap(self):
        for field in self.fields.values():
            if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                continue
            field.widget.attrs.setdefault("class", "form-control")


class GlassTypeForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = GlassType
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()


class StockReceiptForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = StockReceipt
        fields = ["supplier", "doc_no", "date", "note"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "note": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()


class StockSheetForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = StockSheet
        fields = [
            "receipt",
            "glass_type",
            "thickness_mm",
            "width_mm",
            "height_mm",
            "quantity",
            "purchase_price_per_sheet",
            "remaining_area_m2_per_sheet",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()
