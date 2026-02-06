from django.db.models import Count, Sum
from django.shortcuts import render, redirect
from .forms import GlassTypeForm, StockReceiptForm, StockSheetForm, StockIncomeForm
from .models import GlassType, StockReceipt, StockSheet


def glass_type_list(request):
    glass_types = GlassType.objects.all().order_by("name")
    return render(request, "warehouse/glass_type_list.html", {"glass_types": glass_types})


def glass_type_create(request):
    if request.method == "POST":
        form = GlassTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("warehouse:glass_type_list")
    else:
        form = GlassTypeForm()
    return render(request, "warehouse/glass_type_form.html", {"form": form})


def stock_receipt_list(request):
    receipts = StockReceipt.objects.select_related("supplier").all()
    return render(request, "warehouse/stock_receipt_list.html", {"receipts": receipts})


def stock_receipt_create(request):
    if request.method == "POST":
        form = StockReceiptForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("warehouse:stock_receipt_list")
    else:
        form = StockReceiptForm()
    return render(request, "warehouse/stock_receipt_form.html", {"form": form})


def stock_sheet_list(request):
    sheets = StockSheet.objects.select_related("receipt", "glass_type", "receipt__supplier").all()
    summary_by_type = (
        StockSheet.objects.values("glass_type__name")
        .annotate(total_sheets=Sum("quantity"), positions=Count("id"))
        .order_by("glass_type__name")
    )
    return render(
        request,
        "warehouse/stock_sheet_list.html",
        {
            "sheets": sheets,
            "summary_by_type": summary_by_type,
        },
    )


def stock_sheet_create(request):
    if request.method == "POST":
        form = StockSheetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("warehouse:stock_sheet_list")
    else:
        form = StockSheetForm()
    return render(request, "warehouse/stock_sheet_form.html", {"form": form})


def stock_income_create(request):
    if request.method == "POST":
        form = StockIncomeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("warehouse:stock_sheet_list")
    else:
        form = StockIncomeForm()

    return render(request, "warehouse/stock_income_form.html", {"form": form})