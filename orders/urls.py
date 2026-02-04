from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_list, name="list"),
    path("new/", views.order_create, name="create"),
    path("<int:order_id>/", views.order_detail, name="detail"),
    path("<int:order_id>/items/new/", views.order_item_create, name="item_create"),
]
