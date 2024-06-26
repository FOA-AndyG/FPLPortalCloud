import json
import pymysql
import datetime
from datetime import timedelta
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
from django.contrib import messages
import pytz
import numpy as np
from io import BytesIO
from django.http import HttpResponse
import re
import openpyxl
import os
from Django_Project.settings import STATICFILES_DIRS
import xlrd
import xlwt
from xlutils.copy import copy


#********************************************TX************************************************


def tx_ostk_open(conn, conn_wms, conn_cloud):
    orders_q = """SELECT order_code, reference_no, carrier_code, service_level_code, item, qty, tracking_no, retail_order_no, add_time AS received
    FROM orders_record
    WHERE wh_code = 'FPLTX1' AND (status != 'S' AND status != 'H' AND status != 'X' AND status != 'E')"""
    wms_q = """SELECT order_code, order_status FROM wms.orders WHERE warehouse_id = 11 AND customer_code = 'OSTK'"""
    cloud_q = """SELECT tracking_number AS tracking_no, create_date AS scan_time FROM itweb.web_scan_detail where location = 'TX'"""
    orders_df = pd.read_sql_query(orders_q, conn)
    wms_df = pd.read_sql_query(wms_q, conn_wms)
    cloud_df = pd.read_sql_query(cloud_q, conn_cloud)
    new_order_df = orders_df.merge(cloud_df, on='tracking_no', how='left')
    new_order_df = new_order_df.merge(wms_df, on='order_code', how='left')
    print(new_order_df)
    new_order_df.replace([pd.NaT], [None])
    new_order_df['scan_time'] = new_order_df['scan_time'].astype(object).where(new_order_df['scan_time'].notnull(), None)
    return list(new_order_df.itertuples(index=False))


def tx_ostk_shipconfirm(conn, conn_wms, conn_cloud):
    orders_q = """SELECT order_code, reference_no, carrier_code, service_level_code, item, qty, tracking_no, retail_order_no, add_time AS received
    FROM orders_record
    WHERE wh_code = 'FPLTX1' AND status = 'S'"""
    wms_q = """SELECT order_code, order_status FROM wms.orders WHERE warehouse_id = 11 AND customer_code = 'OSTK'"""
    cloud_q = """SELECT tracking_number AS tracking_no, create_date AS scan_time FROM itweb.web_scan_detail where location = 'TX'"""
    orders_df = pd.read_sql_query(orders_q, conn)
    wms_df = pd.read_sql_query(wms_q, conn_wms)
    cloud_df = pd.read_sql_query(cloud_q, conn_cloud)
    new_order_df = orders_df.merge(cloud_df, on='tracking_no', how='left').merge(wms_df, on='order_code', how='left')
    new_order_df.replace([pd.NaT], [None])
    new_order_df['scan_time'] = new_order_df['scan_time'].astype(object).where(new_order_df['scan_time'].notnull(), None)
    return list(new_order_df.itertuples(index=False))


def tx_ostk_error(conn, conn_wms, conn_cloud):
    orders_q = """SELECT order_code, reference_no, carrier_code, service_level_code, item, qty, tracking_no, retail_order_no, add_time AS received
    FROM orders_record
    WHERE wh_code = 'FPLTX1' AND status = 'E'"""
    wms_q = """SELECT order_code, order_status FROM wms.orders WHERE warehouse_id = 11 AND customer_code = 'OSTK'"""
    cloud_q = """SELECT tracking_number AS tracking_no, create_date AS scan_time FROM itweb.web_scan_detail where location = 'TX'"""
    orders_df = pd.read_sql_query(orders_q, conn)
    wms_df = pd.read_sql_query(wms_q, conn_wms)
    cloud_df = pd.read_sql_query(cloud_q, conn_cloud)
    new_order_df = orders_df.merge(cloud_df, on='tracking_no', how='left').merge(wms_df, on='order_code', how='left')
    new_order_df.replace([pd.NaT], [None])
    new_order_df['scan_time'] = new_order_df['scan_time'].astype(object).where(new_order_df['scan_time'].notnull(), None)
    new_order_df['order_status'] = new_order_df['order_status'].astype(object).where(new_order_df['order_status'].notnull(), None)
    return list(new_order_df.itertuples(index=False))


def tx_ostk_export(conn, conn_wms, conn_cloud):
    orders_q = """SELECT order_code, reference_no, carrier_code, service_level_code, item, qty, tracking_no, retail_order_no, status AS api_status, add_time AS received
    FROM orders_record
    WHERE wh_code = 'FPLTX1'"""
    wms_q = """SELECT order_code, order_status FROM wms.orders WHERE warehouse_id = 11 AND customer_code = 'OSTK'"""
    cloud_q = """SELECT tracking_number AS tracking_no, create_date AS scan_time FROM itweb.web_scan_detail where location = 'TX'"""
    orders_df = pd.read_sql_query(orders_q, conn)
    wms_df = pd.read_sql_query(wms_q, conn_wms)
    cloud_df = pd.read_sql_query(cloud_q, conn_cloud)
    new_order_df = orders_df.merge(cloud_df, on='tracking_no', how='left').merge(wms_df, on='order_code', how='left')
    new_order_df.replace([pd.NaT], [None])
    new_order_df['scan_time'] = new_order_df['scan_time'].astype(object).where(new_order_df['scan_time'].notnull(), None)
    new_order_df['order_status'] = new_order_df['order_status'].astype(object).where(new_order_df['order_status'].notnull(), None)

    columns = ['Order Code', 'Reference No', 'Carrier',	'Service Lvl', 'SKU', 'Qty', 'Tracking No', 'Retail Order No', 'api_status', 'Received', 'Scan Time' ,'Status']
    # rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    # df_all = pd.DataFrame(rows)
    new_order_df.columns = columns
    new_order_df['Status'] = new_order_df['Status'].apply(lambda x: 'Submitted' if x == 4 else 'Pulled' if x == 5 else 'Labeled' if x == 7 else 'Issued' if x == 8 else 'Abnormal' if x == 3 else 'Cancelled' if x == 0 else 'New')
    # new_order_df['Status'] = new_order_df['api_status'].apply(lambda x: 'Shortshipped' if (x == 'H') )
    for i in range(0, len(new_order_df['api_status'])):
        if new_order_df['api_status'][i] == 'H':
            new_order_df['Status'][i] = 'Shortshipped'
        elif new_order_df['api_status'][i] == 'E':
            new_order_df['Status'][i] = 'Error'
        elif new_order_df['api_status'][i] == 'X':
            new_order_df['Status'][i] = 'Cancelled'
    del new_order_df['api_status']
    stream_file = BytesIO()
    writer = pd.ExcelWriter(stream_file, engine='xlsxwriter')
    new_order_df.to_excel(writer, sheet_name='TX_OSTK_orders_ALL', index=False)
    for column in new_order_df:
        column_length = max(new_order_df[column].astype(str).map(len).max(), len(column))
        col_idx = new_order_df.columns.get_loc(column)
        writer.sheets['TX_OSTK_orders_ALL'].set_column(col_idx, col_idx, column_length)
    writer.close()
    stream_file.seek(0)
    response = HttpResponse(stream_file, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename="TX_OSTK_orders_ALL.xlsx"'
    return response


#********************************************TX************************************************


def lax_ostk_open(conn, conn_wms, conn_cloud):
    orders_q = """SELECT order_code, reference_no, carrier_code, service_level_code, item, qty, tracking_no, retail_order_no, add_time AS received
    FROM orders_record
    WHERE wh_code = 'FURNITUREPROWH' AND (status != 'S' AND status != 'H' AND status != 'X' AND status != 'E')"""
    wms_q = """SELECT order_code, order_status FROM wms.orders WHERE warehouse_id = 7 AND customer_code = 'OSTK'"""
    cloud_q = """SELECT tracking_number AS tracking_no, create_date AS scan_time FROM itweb.web_scan_detail where location = 'FPL'"""
    orders_df = pd.read_sql_query(orders_q, conn)
    wms_df = pd.read_sql_query(wms_q, conn_wms)
    cloud_df = pd.read_sql_query(cloud_q, conn_cloud)
    new_order_df = orders_df.merge(cloud_df, on='tracking_no', how='left')
    new_order_df = new_order_df.merge(wms_df, on='order_code', how='left')
    print(new_order_df)
    new_order_df.replace([pd.NaT], [None])
    new_order_df['scan_time'] = new_order_df['scan_time'].astype(object).where(new_order_df['scan_time'].notnull(), None)
    return list(new_order_df.itertuples(index=False))


def lax_ostk_shipconfirm(conn, conn_wms, conn_cloud):
    orders_q = """SELECT order_code, reference_no, carrier_code, service_level_code, item, qty, tracking_no, retail_order_no, add_time AS received
    FROM orders_record
    WHERE wh_code = 'FURNITUREPROWH' AND status = 'S'"""
    wms_q = """SELECT order_code, order_status FROM wms.orders WHERE warehouse_id = 7 AND customer_code = 'OSTK'"""
    cloud_q = """SELECT tracking_number AS tracking_no, create_date AS scan_time FROM itweb.web_scan_detail where location = 'FPL'"""
    orders_df = pd.read_sql_query(orders_q, conn)
    wms_df = pd.read_sql_query(wms_q, conn_wms)
    cloud_df = pd.read_sql_query(cloud_q, conn_cloud)
    new_order_df = orders_df.merge(cloud_df, on='tracking_no', how='left').merge(wms_df, on='order_code', how='left')
    new_order_df.replace([pd.NaT], [None])
    new_order_df['scan_time'] = new_order_df['scan_time'].astype(object).where(new_order_df['scan_time'].notnull(), None)
    return list(new_order_df.itertuples(index=False))


def lax_ostk_error(conn, conn_wms, conn_cloud):
    orders_q = """SELECT order_code, reference_no, carrier_code, service_level_code, item, qty, tracking_no, retail_order_no, add_time AS received
    FROM orders_record
    WHERE wh_code = 'FURNITUREPROWH' AND status = 'E'"""
    wms_q = """SELECT order_code, order_status FROM wms.orders WHERE warehouse_id = 7 AND customer_code = 'OSTK'"""
    cloud_q = """SELECT tracking_number AS tracking_no, create_date AS scan_time FROM itweb.web_scan_detail where location = 'FPL'"""
    orders_df = pd.read_sql_query(orders_q, conn)
    wms_df = pd.read_sql_query(wms_q, conn_wms)
    cloud_df = pd.read_sql_query(cloud_q, conn_cloud)
    new_order_df = orders_df.merge(cloud_df, on='tracking_no', how='left').merge(wms_df, on='order_code', how='left')
    new_order_df.replace([pd.NaT], [None])
    new_order_df['scan_time'] = new_order_df['scan_time'].astype(object).where(new_order_df['scan_time'].notnull(), None)
    new_order_df['order_status'] = new_order_df['order_status'].astype(object).where(new_order_df['order_status'].notnull(), None)
    return list(new_order_df.itertuples(index=False))


def lax_ostk_export(conn, conn_wms, conn_cloud):
    orders_q = """SELECT order_code, reference_no, carrier_code, service_level_code, item, qty, tracking_no, retail_order_no, status AS api_status, add_time AS received
    FROM orders_record
    WHERE wh_code = 'FURNITUREPROWH'"""
    wms_q = """SELECT order_code, order_status FROM wms.orders WHERE warehouse_id = 7 AND customer_code = 'OSTK'"""
    cloud_q = """SELECT tracking_number AS tracking_no, create_date AS scan_time FROM itweb.web_scan_detail where location = 'FPL'"""
    orders_df = pd.read_sql_query(orders_q, conn)
    wms_df = pd.read_sql_query(wms_q, conn_wms)
    cloud_df = pd.read_sql_query(cloud_q, conn_cloud)
    new_order_df = orders_df.merge(cloud_df, on='tracking_no', how='left').merge(wms_df, on='order_code', how='left')
    new_order_df.replace([pd.NaT], [None])
    new_order_df['scan_time'] = new_order_df['scan_time'].astype(object).where(new_order_df['scan_time'].notnull(), None)
    new_order_df['order_status'] = new_order_df['order_status'].astype(object).where(new_order_df['order_status'].notnull(), None)

    columns = ['Order Code', 'Reference No', 'Carrier',	'Service Lvl', 'SKU', 'Qty', 'Tracking No', 'Retail Order No', 'api_status', 'Received', 'Scan Time' ,'Status']
    # rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    # df_all = pd.DataFrame(rows)
    new_order_df.columns = columns
    new_order_df['Status'] = new_order_df['Status'].apply(lambda x: 'Submitted' if x == 4 else 'Pulled' if x == 5 else 'Labeled' if x == 7 else 'Issued' if x == 8 else 'Abnormal' if x == 3 else 'Cancelled' if x == 0 else 'New')
    # new_order_df['Status'] = new_order_df['api_status'].apply(lambda x: 'Shortshipped' if (x == 'H') )
    for i in range(0, len(new_order_df['api_status'])):
        if new_order_df['api_status'][i] == 'H':
            new_order_df['Status'][i] = 'Shortshipped'
        elif new_order_df['api_status'][i] == 'E':
            new_order_df['Status'][i] = 'Error'
        elif new_order_df['api_status'][i] == 'X':
            new_order_df['Status'][i] = 'Cancelled'
    del new_order_df['api_status']
    stream_file = BytesIO()
    writer = pd.ExcelWriter(stream_file, engine='xlsxwriter')
    new_order_df.to_excel(writer, sheet_name='LAX_OSTK_orders_ALL', index=False)
    for column in new_order_df:
        column_length = max(new_order_df[column].astype(str).map(len).max(), len(column))
        col_idx = new_order_df.columns.get_loc(column)
        writer.sheets['LAX_OSTK_orders_ALL'].set_column(col_idx, col_idx, column_length)
    writer.close()
    stream_file.seek(0)
    response = HttpResponse(stream_file, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename="LAX_OSTK_orders_ALL.xlsx"'
    return response
