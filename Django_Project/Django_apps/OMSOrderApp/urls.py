from django.urls import path, re_path
from django.views.generic import RedirectView

from Django_apps.OMSOrderApp import views

app_name = 'OMSOrderApp'


urlpatterns = [

    path('', views.dashboard, name='dashboard'),
    re_path(r'^dashboard/', RedirectView.as_view(pattern_name='dashboard', permanent=False)),

    # path('order_page/', views.order_page, name='order_page'),
    # path('new_order_page/', views.new_order_page, name='new_order_page'),
    # path('new_label_import_page/', views.new_label_import_page, name='new_label_import_page'),
    # path('container_detail_label_page/', views.container_detail_label_page, name='container_detail_label_page'),
    #
    # # path('download_order_attachment_page/', views.download_order_attachment_page, name='download_order_attachment_page'),
    # path('new_download_order_attachment_page/', views.new_download_order_attachment_page,
    #      name='new_download_order_attachment_page'),
    # path('picking_detail_download_ajax/', views.picking_detail_download_ajax,
    #      name='picking_detail_download_ajax'),
    #
    # path('order_status_page/', views.order_status_page, name='order_status_page'),
    # path('tracking_finder/', views.tracking_finder, name='tracking_finder'),
    # path('fpl_fdw_order_process/', views.fpl_fdw_order_process, name='fpl_fdw_order_process'),

    path('pdf_merge_page/', views.pdf_merge_page, name='pdf_merge_page'),
    # path('storage_fee_calculator/', views.storage_fee_calculator, name='storage_fee_calculator'),


    # scan program
    path('web_scan_page/', views.web_scan_page, name='web_scan_page'),
    path('web_scan_detail_page/<str:trailer_number>', views.web_scan_detail_page, name='web_scan_detail_page'),
    path('web_scan_function/', views.web_scan_function, name='web_scan_function'),
    path('web_scan_wrong_tracking_page/', views.web_scan_wrong_tracking_page, name='web_scan_wrong_tracking_page'),
    path('web_scan_report/', views.web_scan_report, name='web_scan_report'),
    path('web_scan_checking_page/', views.web_scan_checking_page, name='web_scan_checking_page'),
    path('web_scan_printing_page/', views.web_scan_printing_page, name='web_scan_printing_page'),

    # url(r'^web_scan_wrong_tracking_page/(?P<tracking>\d+)$', views.web_scan_wrong_tracking_page,
    #     name='web_scan_wrong_tracking_page'),

    # # report
    # path('container_report/', views.container_report, name='container_report'),
    # path('scan_report/', views.scan_report, name='scan_report'),
    # path('branch_order_sales_report/', views.branch_order_sales_report, name='branch_order_sales_report'),
    # path('check_in_page/', views.check_in_page, name='check_in_page'),
    # path('fpl_direct_sale_pricing_log/', views.fpl_direct_sale_pricing_log, name='fpl_direct_sale_pricing_log'),
    # path('scan_error_report/', views.scan_error_report, name='scan_error_report'),
    #
    # # picking pages
    # path('picking_page/', views.picking_page, name='picking_page'),

]
