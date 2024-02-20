from django.urls import path

from Django_apps.OSTKApiApp import views

app_name = 'OSTKApiApp'

urlpatterns = [
    path("ostk_inventory/", views.ostk_inventory, name="ostk_inventory"),
    path("ostk_po_receipt/", views.ostk_po_receipt, name="ostk_po_receipt"),
    path("tx_ostk_orders/", views.tx_ostk_orders, name="tx_ostk_orders"),
    path("lax_ostk_orders/", views.lax_ostk_orders, name="lax_ostk_orders"),
    path("ostk_po_import/", views.ostk_po_import, name="ostk_po_import"),
    path("ostk_upc_export/", views.ostk_upc_export, name="ostk_upc_export"),
    path("ostk_adj/", views.ostk_adj, name="ostk_adj"),
    path("ostk_sh/", views.ostk_sh, name="ostk_sh"),
    path("ostk_overages/", views.ostk_overages, name="ostk_overages"),
    path('ostk_po_receipt/<str:receiving_code>/', views.ostk_po_receipt_popup, name="ostk_po_receipt")
]
