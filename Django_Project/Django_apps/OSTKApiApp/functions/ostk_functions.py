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
from .sql_connection import *

def get_today_adjustments():
    testing = False
    conn = wms_mysql_connection()
    cursor = conn.cursor()
    conn2 = mysql_connection()
    cursor2 = conn2.cursor()
    f_data = []
    if testing:
        q = """SELECT * FROM product_inventory_log_test WHERE pil_add_time >= NOW() - INTERVAL 1 DAY"""
        cursor2.execute(q)
        data = cursor2.fetchall()
    else:
        q = """SELECT pil_id, product_barcode, pil_quantity, pil_add_time, warehouse_id FROM product_inventory_log WHERE application_code='adjustInventory' AND warehouse_id = 11 AND pil_add_time >= NOW() - INTERVAL 1 DAY"""
        cursor.execute(q)
        data = cursor.fetchall()
    for product in data:
        id = product[0]
        item = product[1].replace('OSTK-', '')
        open_adj_q = f"""SELECT * FROM adj_tracker WHERE pil_id = '{id}'"""
        cursor2.execute(open_adj_q)
        exist_id = cursor2.fetchone()
        if exist_id is None:
            f_data.append((id, item, product[2], product[3], product[4]))
    return f_data

def get_adj_history():
    conn = mysql_connection()
    cursor = conn.cursor()

    adj_history_q = """SELECT product_barcode, qty, reason_code, add_time FROM adj_reasoning ORDER BY add_time desc"""

    cursor.execute(adj_history_q)
    history = cursor.fetchall()
    return history

def ostk_upc_export(request):
    conn = mysql_connection()
    testing = False
    if testing:
        prefix = 'FPTEST-'
    else:
        prefix = 'OSTK-'
    products_q = """SELECT product_barcode, ref FROM products_test WHERE update_time IS NOT NULL"""
    products_df = pd.read_sql_query(products_q, conn)
    column1 = products_df.columns[0]
    column2 = products_df.columns[1]
    for i in range(0, len(products_df[column1])):
        products_df[column1][i] = prefix + products_df[column1][i]
    stream_file = BytesIO()
    excel = os.path.join(STATICFILES_DIRS[0], 'programtools\\template\\ostk_upc_template.xls')
    book = xlrd.open_workbook(excel, formatting_info=True)
    sheet = book.sheet_by_index(0)

    wb = copy(book)
    sheet = wb.get_sheet(0)
    for i in range(0, len(products_df[column1])):
        sheet.write(i+1, 0, products_df[column1][i])
        sheet.write(i+1, 1, products_df[column2][i])
    wb.save('upc_export.xls')
    stream_file = open('upc_export.xls', "rb")
    response = HttpResponse(stream_file, content_type='application/vnd.ms-excel')
    stream_file.close()
    response['Content-Disposition'] = 'attachment;filename="OSTK_UPC.xlsx"'

    conn.close()

    return response


def import_ostk_po_func(request, df):
    testing = False
    conn = mysql_connection()
    cursor = conn.cursor()
    if testing:
        track_sub_name = 'po_sub_test'
    else:
        track_sub_name = 'po_sub'
    try:
        # has to be a day ahead to push to WMS
        current_date = datetime.datetime.now() + timedelta(days=1)
        eta_check = current_date.strftime("%Y-%m-%d")
        df_final = pd.DataFrame()
        for index, row in df.iterrows():
            print(index)
            if row['Appointment Date'] == 'PENDING':
                print("match")
                df_final = df[:index]
                break
        df_final.dropna(axis=0, how='all', inplace=True)
        df_final['Appointment Date'] = pd.to_datetime(df_final['Appointment Date']).dt.strftime('%Y-%m-%d')
        val = []
        df_final = df_final.replace({np.nan: None})
        print(df_final[['Appointment Date', 'Vendor PO #', 'Confirmation #']])
        late = []
        for index, row in df_final.iterrows():
            dt = row['Appointment Date']
            ref = row['Warehouse PO #']
            tracking = row['Confirmation #']
            if ref:
                print(eta_check, dt)
                check_status_q = f"""SELECT status FROM {track_sub_name} WHERE master_ref_no = '{ref}' GROUP BY status"""
                cursor.execute(check_status_q)
                status = cursor.fetchone()
                if eta_check <= dt and status[0] == 'O':
                    if ref != None and tracking != None:
                        val.append((dt, tracking, ref))
                else:
                    print("raise")
                    late.append(ref)
        q = """UPDATE {track_sub_name} SET eta = %s, tracking_no = %s WHERE master_ref_no = %s AND status = 'O'""".format(track_sub_name=track_sub_name)
        cursor.executemany(q, val)
    except Exception as e:
        print(e)
        conn.rollback()
        messages.error(request, f"File Upload Failed {str(e)}")
    else:
        print("commit")
        conn.commit()
        messages.success(request, "File Upload Success")
        if late:
            messages.warning(request, f"REF: {late} - Failed")
    finally:
        cursor.close()
        conn.close()


def manual_shortship(request):
    master_ref_no = request.GET.get("order_code")
    print("master_ref_no", master_ref_no)
    conn = mysql_connection()
    cursor = conn.cursor()
    testing = False

    if testing:
        order_record_name = 'orders_record_test'
        overstock_url = "https://inbound-warehouse-transaction-ws.overstock.com/shortShip"
        basic = HTTPBasicAuth('furnitureofamerica', '#N5A9CmSWCoFT5do`cigE3n7J')
    else:
        order_record_name = 'orders_record'
        overstock_url = "https://api.bedbathandbeyond.com/inbound-warehouse-transaction-ws/shortShip"
        basic = HTTPBasicAuth('furnitureofamerica', 'Q9fEiazCcEoX%Dt$zY3k#7#3P')

    q_log = """INSERT script_logger (response_name, response_code, status, data) VALUES (%s, %s, %s, %s)"""
    try:
        q = f"""SELECT wh_code FROM {order_record_name} WHERE master_ref_no = '{master_ref_no}' GROUP BY wh_code"""
        cursor.execute(q)
        wh_code = cursor.fetchone()
        container = {
            "organizationId": "FOA",
            "warehouseName": wh_code[0],
            "salesOrderId": master_ref_no, # reference_no
            "details": []
        }

        get_order_qty_q = f"""SELECT item, CASE WHEN carrier_type <> 'LTL' THEN COUNT(*) ELSE qty END AS qty, line_no FROM {order_record_name} WHERE master_ref_no = '{master_ref_no}' GROUP BY item"""
        cursor.execute(get_order_qty_q)
        orders_qty_obj = cursor.fetchall()
        for item in orders_qty_obj:
            container['details'].append({
                "salesChannelLineNumber": item[2],
                "warehouseSku": item[0],
                "orderQuantity": item[1]
            }) #append dictionary

        shipconfirm_controller = {
            "orders": [container]
        }
        print(shipconfirm_controller)
    except Exception as e:
        print(e)
        cursor.execute(q_log, ("shortship", 500, "Failure", f"{e}"))
        conn.commit()
        messages.error(request, f"{e}")
    else:
        q2 = f"""UPDATE {order_record_name} SET status = 'H' WHERE master_ref_no = '{master_ref_no}'"""
        cursor.execute(q2)
        if testing is False:
            response = requests.post(overstock_url, json=shipconfirm_controller, auth=basic)
            print("----------------------response-------------------------")
            print(response)
            print("----------------------response-------------------------")
        status = response.status_code
        if status == 200:
            cursor.execute(q_log, ("shortship", status, "Success", json.dumps(shipconfirm_controller, indent=4)))
        else:
            cursor.execute(q_log, ("shortship", status, "Failure", json.dumps(shipconfirm_controller, indent=4)))
        conn.commit()
        messages.success(request, f"{master_ref_no} Order Shortshipped")
    finally:
        cursor.close()
        conn.close()


def get_order_codes():
    print("order")
    testing = False

    if testing:
        order_record_name = 'orders_record_test'
    else:
        order_record_name = 'orders_record'

    q = f"""SELECT wh_code, carrier_code, master_ref_no FROM {order_record_name} WHERE status <> 'S' and status <> 'H' and status <> 'X' GROUP BY master_ref_no ORDER BY add_time desc"""

    conn = mysql_connection()
    cursor = conn.cursor()
    cursor.execute(q)
    container = cursor.fetchall()
    content = []
    for o_code in container:
        wh = o_code[0]
        carrier = o_code[1]
        ref = o_code[2]
        content.append((wh, carrier, ref))
    cursor.close()
    conn.close()
    return content
    # send to ui when page opens


def get_order_codes_by_ref(ref):
    testing = False

    if testing:
        order_record_name = 'orders_record_test'
    else:
        order_record_name = 'orders_record'

    q = f"""SELECT order_code, reference_no, item FROM {order_record_name} WHERE status <> 'S' and status <> 'H' and status <> 'X' AND master_ref_no = '{ref}' ORDER BY add_time desc"""

    conn = mysql_connection()
    cursor = conn.cursor()
    cursor.execute(q)
    container = cursor.fetchall()
    cursor.close()
    conn.close()
    return container