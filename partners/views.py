from django.shortcuts import render, redirect
from .forms import PartnerForm
from .models import Partner


def partner_list(request):
    partners = Partner.objects.all().order_by("partner_type", "name")
    return render(request, "partners/partner_list.html", {"partners": partners})


def partner_create(request):
    if request.method == "POST":
        form = PartnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("partners:list")
    else:
        form = PartnerForm()
    return render(request, "partners/partner_form.html", {"form": form})
