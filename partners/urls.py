from django.urls import path
from . import views

app_name = "partners"

urlpatterns = [
    path("", views.partner_list, name="list"),
    path("new/", views.partner_create, name="create"),
]
