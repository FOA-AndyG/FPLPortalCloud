from django.urls import path, re_path
from django.views.generic import RedirectView

from Django_apps.TicketApp import views

app_name = 'TicketApp'


urlpatterns = [

    path('landing_view/', views.landing_view, name='landing_view'),

    path("storage_create/", views.storage_create_view, name="storage_create"),
    path("storage_search/", views.storage_search_view, name="storage_search"),
    path("storage_confirm/<int:record_id>/", views.storage_confirm_view, name="storage_confirm"),
    path("storage_logs/<int:record_id>/", views.storage_logs_view, name="storage_logs"),

]
