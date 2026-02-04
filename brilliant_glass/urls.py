from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from brilliant_glass import settings
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", admin.site.urls),
    path("partners/", include("partners.urls")),
    path("warehouse/", include("warehouse.urls")),
    path("orders/", include("orders.urls")),
    path("finance/", include("finance.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
