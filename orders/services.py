from decimal import Decimal
from django.db import transaction
from warehouse.models import StockSheet
from .models import Order, OrderItem, StockConsumption

class NotEnoughStock(Exception):
    pass

@transaction.atomic
def allocate_stock_for_item(item: OrderItem):
    need_area = item.area_m2_total()  # сколько м2 надо под позицию

    # Берём листы подходящего типа/толщины (FIFO по created_at)
    sheets = (StockSheet.objects
              .select_for_update()
              .filter(
                  glass_type=item.glass_type,
                  thickness_mm=item.thickness_mm,
                  remaining_area_m2_per_sheet__gt=0
              )
              .order_by("created_at"))

    for sheet in sheets:
        if need_area <= 0:
            break

        # сколько можем взять с этого листа (учитываем quantity)
        total_available = sheet.total_remaining_area_m2()

        if total_available <= 0:
            continue

        take = min(need_area, total_available)

        # Списание делаем “с листов” пропорционально:
        # упрощенно уменьшаем remaining_area_m2_per_sheet
        # (если quantity > 1 — корректнее вести отдельные листы, но стартуем так)
        per_sheet_available = Decimal(sheet.remaining_area_m2_per_sheet)
        if per_sheet_available <= 0:
            continue

        # Уменьшаем остаток на одном листе, пока не спишем нужное
        # Простое приближение: уменьшаем remaining_area_m2_per_sheet на take/quantity
        delta_per_sheet = (Decimal(take) / Decimal(sheet.quantity))

        new_remaining = per_sheet_available - delta_per_sheet
        if new_remaining < 0:
            new_remaining = Decimal("0")

        sheet.remaining_area_m2_per_sheet = new_remaining
        sheet.save(update_fields=["remaining_area_m2_per_sheet"])

        StockConsumption.objects.create(
            order_item=item,
            stock_sheet=sheet,
            consumed_area_m2=take
        )

        need_area -= Decimal(take)

    if need_area > 0:
        raise NotEnoughStock(f"Not enough stock for item {item.id}: missing {need_area} m2")


@transaction.atomic
def allocate_stock_for_order(order: Order):
    for item in order.items.select_for_update():
        allocate_stock_for_item(item)