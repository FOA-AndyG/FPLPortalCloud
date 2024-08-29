from django.urls import path, re_path
from django.views.generic import RedirectView

from Django_apps.TicketApp import views

app_name = 'TicketApp'


urlpatterns = [

    path('ticket_dashboard/', views.ticket_dashboard, name='ticket_dashboard'),
    path('create_ticket/', views.create_ticket, name='create_ticket'),

    path('ticket_list/', views.ticket_list, name='ticket_list'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),

]
