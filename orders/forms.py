from django import forms
from .models import Order, OrderItem


class FormControlMixin:
    def apply_bootstrap(self):
        for field in self.fields.values():
            if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                continue
            field.widget.attrs.setdefault("class", "form-control")


class OrderForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = Order
        fields = ["client", "status", "date", "note"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "note": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()


class OrderItemForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = [
            "glass_type",
            "thickness_mm",
            "width_mm",
            "height_mm",
            "quantity",
            "sale_price",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()
