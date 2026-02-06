from django import forms
from django.utils import timezone
from partners.models import Partner
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


class StockIncomeForm(FormControlMixin, forms.Form):
    supplier = forms.ModelChoiceField(
        queryset=Partner.objects.filter(partner_type=Partner.SUPPLIER).order_by("name"),
        label="Поставщик",
    )
    date = forms.DateField(
        label="Дата прихода",
        widget=forms.DateInput(attrs={"type": "date"}),
        initial=timezone.localdate,
    )
    doc_no = forms.CharField(max_length=80, required=False, label="№ документа")
    note = forms.CharField(required=False, label="Комментарий", widget=forms.Textarea(attrs={"rows": 2}))

    glass_type = forms.ModelChoiceField(queryset=GlassType.objects.order_by("name"), label="Тип стекла")
    thickness_mm = forms.IntegerField(min_value=1, label="Толщина (мм)")
    width_mm = forms.IntegerField(min_value=1, label="Ширина (мм)")
    height_mm = forms.IntegerField(min_value=1, label="Высота (мм)")
    quantity = forms.IntegerField(min_value=1, initial=1, label="Количество листов")
    purchase_price_per_sheet = forms.DecimalField(min_value=0, decimal_places=2, max_digits=14, label="Цена за лист")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()

        self.fields["width_mm"].widget.attrs["id"] = "id_width_mm"
        self.fields["height_mm"].widget.attrs["id"] = "id_height_mm"
        self.fields["quantity"].widget.attrs["id"] = "id_quantity"
        self.fields["purchase_price_per_sheet"].widget.attrs["id"] = "id_purchase_price_per_sheet"

    def save(self):
        receipt = StockReceipt.objects.create(
            supplier=self.cleaned_data["supplier"],
            date=self.cleaned_data["date"],
            doc_no=self.cleaned_data["doc_no"],
            note=self.cleaned_data["note"],
        )
        return StockSheet.objects.create(
            receipt=receipt,
            glass_type=self.cleaned_data["glass_type"],
            thickness_mm=self.cleaned_data["thickness_mm"],
            width_mm=self.cleaned_data["width_mm"],
            height_mm=self.cleaned_data["height_mm"],
            quantity=self.cleaned_data["quantity"],
            purchase_price_per_sheet=self.cleaned_data["purchase_price_per_sheet"],
        )