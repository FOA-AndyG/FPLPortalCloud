from django.urls import path, re_path
from django.views.generic import RedirectView

from Django_apps.HomeApp import views

app_name = 'HomeApp'


urlpatterns = [

    path('', views.login, name='login'),

    path('login/', views.login, name='login'),
    path('login/', RedirectView.as_view(pattern_name='login', permanent=False)),

    path('logout/', views.logout, name='logout'),

    # path('home/', views.home, name='home'),
    # re_path(r'^home/', RedirectView.as_view(pattern_name='home', permanent=False)),

    # path('new_home_page/', views.new_home_page, name='new_home_page'),

    # # dashboard
    # path('dashboard_total_upcoming_container_ajax/', views.dashboard_total_upcoming_container_ajax,
    #      name='dashboard_total_upcoming_container_ajax'),


]
