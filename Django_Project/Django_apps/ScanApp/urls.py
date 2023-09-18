from django.urls import path
from django.views.generic import RedirectView

from Django_apps.ScanApp import views

app_name = 'ScanApp'


urlpatterns = [
    path("", views.index, name="index"),
    path("<str:trailer_number>/", views.trailer_page, name="trailer_page"),
    path("scan_info_import", views.scan_info_import, name="scan_info_import")
]
