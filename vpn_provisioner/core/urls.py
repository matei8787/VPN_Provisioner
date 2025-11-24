from django.urls import path
from .views import index_view, vpn_export_view
urlpatterns = [
    path('index/', index_view, name="index"),
    path('download/', vpn_export_view, name="export")
]
