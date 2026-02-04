from django import forms
from .models import Partner


class FormControlMixin:
    def apply_bootstrap(self):
        for field in self.fields.values():
            if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                continue
            field.widget.attrs.setdefault("class", "form-control")


class PartnerForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = Partner
        fields = ["partner_type", "name", "phone", "address", "note"]
        widgets = {
            "note": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()
