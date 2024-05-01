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


"""
Inbound Operator Error (Receiving Error)                                76 +1
Product Damaged (After Receipt) – Found during cycle count              73 -1
Overages (After Receipt) – Found during cycle count                     1  +1
Shortages (After Receipt) – Found during cycle count                    1  -1
Return Back to Stock - Returns that are good to adjust back to stock    65 +1
"""

controller = {
    "Inbound Operator Error": 76,
    "Product Damaged": 73,
    "Overages": 1,
    "Shortages": 1,
    "Return Back to Stock": 65
}


def create(request, id, wh, sku, qty, reason_code):
    testing = False
    adj_name = 'adj_reasoning'
    status = 500
    if testing:
        overstock_url = "https://inbound-warehouse-transaction-ws.overstock.com/inventoryAdjustment"
        basic = HTTPBasicAuth('furnitureofamerica', '#N5A9CmSWCoFT5do`cigE3n7J')
    else:
        overstock_url = "https://api.bedbathandbeyond.com/inbound-warehouse-transaction-ws/inventoryAdjustment"
        basic = HTTPBasicAuth('furnitureofamerica', 'Q9fEiazCcEoX%Dt$zY3k#7#3P')
    conn = mysql_connection()
    cursor = conn.cursor()
    try:
        ref = request.POST.get("ref", "SELLABLE")
        trans_code = int(request.POST.get("trans_code", 852))
        # qty should be always positive
        # if qty < 0:
        #     qty = -(qty)
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        naive = datetime.datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S")
        utc_dt = naive.astimezone(pytz.utc)
        utc_format = utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
        # if reason_code == "Product Damaged" or reason_code == "Shortages":
        #     filter_qty = -qty
        # else:
        #     filter_qty = qty
        filter_qty = qty
        q = """INSERT {adj_name} (wh_id, product_barcode, ref, trans_code, qty, reason_code, add_time) VALUES (%s, %s, %s, %s, %s, %s, %s)""".format(
            adj_name=adj_name)
        cursor.execute(q, (wh, sku, ref, trans_code, filter_qty, reason_code, current_date,))
        container = []
        q2 = """SELECT id, add_time FROM {adj_name} WHERE add_time = %s""".format(adj_name=adj_name)
        cursor.execute(q2, (current_date,))
        uid, d = cursor.fetchone()
        current_time_format = datetime.datetime.strftime(d, "%Y-%m-%dT%H:%M:%S.%f%z") + "Z"
        container.append({
            "warehouseSku": sku,  # product
            "transactionCode": str(trans_code),
            "firstControlNumber": str(controller[reason_code]),
            "transactionQuantity": filter_qty,
            "transactionDate": utc_format,
            "firstLocationId": ref,
            "uid": str(uid),
        })
        q3 = f"""SELECT wh_code FROM wh_xref WHERE warehouse_id = {wh}"""
        cursor.execute(q3)
        wh_code = cursor.fetchone()
        if len(wh_code) == 0:
            raise Exception(f"no warehouse xref {wh}")
        snap_request = {
            'organizationId': 'FOA',
            'warehouseName': wh_code[0],
            'inventoryAdjustments': container
        }

        print(snap_request)

    except Exception as e:
        conn.rollback()
        print(e)
        q = """INSERT script_logger (response_name, response_code, status, data, response_data) VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(q, ("inv_adj", 500, "Failure", json.dumps(snap_request, indent=4), f"{e}"))
        conn.commit()
    else:
        if testing is False:
            response = requests.post(overstock_url, json=snap_request, auth=basic)
            print("----------------------response-------------------------")
            print(response)
            print("----------------------response-------------------------")
        status = response.status_code
        if status == 200:
            stat_txt = 'Success'
            record_id(id, cursor)
        else:
            stat_txt = 'Failure'
            record_id(id, cursor)
            conn.rollback()
        q = """INSERT script_logger (response_name, response_code, status, data, response_data) VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(q, ("inv_adj", status, stat_txt, json.dumps(snap_request, indent=4), None))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
        return status

def record_id(id, cursor):
    q = f"""INSERT INTO adj_tracker (pil_id) VALUES ('{id}')"""
    cursor.execute(q)

def get_today_adjustments():
    testing = False
    conn = wms_mysql_connection()
    cursor = conn.cursor()
    conn2 = mysql_connection()
    cursor2 = conn2.cursor()
    f_data = []
    if testing:
        q = """SELECT t.*, w.wh_code FROM ostk_fpl.product_inventory_log_test t
        left join ostk_fpl.wh_xref w on t.warehouse_id = w.warehouse_id
        WHERE pil_add_time >= NOW() - INTERVAL 3 DAY"""
        cursor2.execute(q)
        data = cursor2.fetchall()
    else:
        wh_id_q = """SELECT warehouse_id FROM wh_xref"""
        cursor2.execute(wh_id_q)
        wh_id_data = cursor2.fetchall()
        indx = 0
        wh_size = len(wh_id_data) - 1
        # grab the warehouse ID in wh_xref table
        warehouse_string = f"i.warehouse_id = {wh_id_data[indx][0]}"
        while indx < wh_size:
            indx += 1
            warehouse_string += f" OR i.warehouse_id = {wh_id_data[indx][0]}"
        for wh_id in wh_id_data:
            id = wh_id[0]
            warehouse_string += ""
        # q = f"""SELECT pil_id, product_barcode, pil_quantity, pil_add_time, warehouse_id FROM product_inventory_log WHERE application_code='adjustInventory' AND pil_add_time >= NOW() - INTERVAL 1 DAY AND ({warehouse_string})"""
        q = f"""SELECT x.pil_id, x.product_barcode, x.pil_quantity, x.pil_add_time, x.warehouse_id, w.warehouse_code FROM(
            SELECT i.pil_id, i.product_barcode, i.pil_quantity, i.pil_add_time, i.warehouse_id FROM product_inventory_log i
            WHERE i.application_code='adjustInventory' AND i.product_barcode LIKE 'OSTK%' AND i.pil_add_time >= NOW() - INTERVAL 15 DAY AND ({warehouse_string})
            UNION
            SELECT d.rd_id, d.product_barcode, d.rd_putaway_qty, d.rd_update_time, r.warehouse_id from receiving_detail AS d
            LEFT JOIN (SELECT warehouse_id, receiving_code FROM receiving) AS r ON r.receiving_code = d.receiving_code
            WHERE d.receiving_code LIKE 'RMA%' AND d.product_barcode LIKE 'OSTK%' ) x
            LEFT JOIN warehouse w ON x.warehouse_id = w.warehouse_id"""
        # q = f"""SELECT i.pil_id, i.product_barcode, i.pil_quantity, i.pil_add_time, i.warehouse_id, w.warehouse_code FROM product_inventory_log i
        #     LEFT JOIN warehouse w ON i.warehouse_id = w.warehouse_id
        #     WHERE i.application_code='adjustInventory' AND i.pil_add_time >= NOW() - INTERVAL 3 DAY AND i.product_barcode LIKE 'OSTK%' AND ({warehouse_string})
        #     UNION
        #     select rd_id, product_barcode, rd_putaway_qty, rd_update_time, 0 AS warehouse_id, 'RETURN' AS warehouse_code from receiving_detail where receiving_code LIKE 'RMA%' AND product_barcode LIKE 'OSTK%'"""
        print(q)
        cursor.execute(q)
        data = cursor.fetchall()
    for product in data:
        id = product[0]
        item = product[1].replace('OSTK-', '')
        open_adj_q = f"""SELECT * FROM adj_tracker WHERE pil_id = '{id}'"""
        cursor2.execute(open_adj_q)
        exist_id = cursor2.fetchone()
        if exist_id is None:
            f_data.append((id, item, product[2], product[3], product[4], product[5]))
    return f_data

def get_adj_history():
    conn = mysql_connection()
    cursor = conn.cursor()

    adj_history_q = """
    SELECT i.wh_code, product_barcode, qty, reason_code, add_time FROM ostk_fpl.adj_reasoning h
    LEFT JOIN ostk_fpl.wh_xref i ON h.wh_id = i.warehouse_id
    ORDER BY add_time desc
    """

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
                print(eta_check, dt, ref)
                check_status_q = f"""SELECT status FROM {track_sub_name} WHERE master_ref_no = '{ref}' GROUP BY status"""
                cursor.execute(check_status_q)
                status = cursor.fetchone()
                if status == None:
                    raise Exception(f"{ref} does not exist")
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
        messages.warning(request, f"File Upload Failed {str(e)}")
    else:
        print("commit")
        conn.commit()
        if late:
            messages.success(request, "File Upload Partial Success")
            messages.warning(request, f"REF: {late} - Failed")
        else:
            messages.success(request, "File Upload Success")
    finally:
        cursor.close()
        conn.close()


def manual_shortship(request):
    master_ref_no = request.POST.get("order_code")
    print("master_ref_no", master_ref_no)
    conn = mysql_connection()
    cursor = conn.cursor()
    testing = False
    current_date_obj = datetime.datetime.now()
    current_date = current_date_obj.strftime("%Y-%m-%d %H:%M:%S")

    if testing:
        order_record_name = 'orders_record_test'
        overstock_url = "https://inbound-warehouse-transaction-ws.overstock.com/shortShip"
        basic = HTTPBasicAuth('furnitureofamerica', '#N5A9CmSWCoFT5do`cigE3n7J')
    else:
        order_record_name = 'orders_record'
        overstock_url = "https://api.bedbathandbeyond.com/inbound-warehouse-transaction-ws/shortShip"
        basic = HTTPBasicAuth('furnitureofamerica', 'Q9fEiazCcEoX%Dt$zY3k#7#3P')

    q_log = """INSERT script_logger (response_name, response_code, status, data, response_data) VALUES (%s, %s, %s, %s, %s)"""
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

        get_order_qty_q = f"""SELECT item, CASE WHEN carrier_type <> 'LTL' THEN COUNT(*) ELSE qty END AS qty, line_no FROM {order_record_name} WHERE master_ref_no = '{master_ref_no}' and status <> 'S' and status <> 'H' and status <> 'X' GROUP BY item"""
        cursor.execute(get_order_qty_q)
        orders_qty_obj = cursor.fetchall()
        for item in orders_qty_obj:
            container['details'].append({
                "salesChannelLineNumber": item[2],
                "warehouseSku": item[0],
                "orderQuantity": item[1]
            }) #append dictionary
            q2 = f"""UPDATE {order_record_name} SET status = 'H', latest_shipdate = '{current_date_obj}' WHERE master_ref_no = '{master_ref_no}' and item = '{item[0]}'"""
            cursor.execute(q2)

        shipconfirm_controller = {
            "orders": [container]
        }
        print(shipconfirm_controller)
    except Exception as e:
        print(e)
        conn.rollback()
        cursor.execute(q_log, ("shortship", 500, "Failure", json.dumps(shipconfirm_controller, indent=4), f"{e}"))
        conn.commit()
        messages.error(request, f"{e}")
    else:
        if testing is False:
            response = requests.post(overstock_url, json=shipconfirm_controller, auth=basic)
            print("----------------------response-------------------------")
            print(response)
            print("----------------------response-------------------------")
            status = response.status_code
            if status == 200:
                cursor.execute(q_log, ("shortship", status, "Success", json.dumps(shipconfirm_controller, indent=4), None))
            else:
                cursor.execute(q_log, ("shortship", status, "Failure", json.dumps(shipconfirm_controller, indent=4), None))
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


def get_overages():
    conn = mysql_connection()
    cursor = conn.cursor()
    testing = False
    if testing:
        po_overage_name = 'po_overage_logger_test'
    else:
        po_overage_name = 'po_overage_logger'
    get_overages_q = f"""SELECT receiving_code, wh_code, master_ref_no, product_barcode, wms_qty, received_qty, ostk_qty, line_no FROM {po_overage_name} where status = 'O'"""
    cursor.execute(get_overages_q)
    container = cursor.fetchall()
    cursor.close()
    conn.close()
    return container , len(container)

def manual_overage(request):
    wh_code = request.POST.get("wh_code")
    reference_no = request.POST.get("ref")
    line_no = request.POST.get("line_no")
    sku = request.POST.get("sku")
    recqty = int(request.POST.get("recqty"))
    ostkqty = int(request.POST.get("ostkqty"))
    qty = int(request.POST.get("qty"))
    current_date_obj = datetime.datetime.now()
    current_date = current_date_obj.strftime("%Y-%m-%d %H:%M:%S")
    naive = datetime.datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S")
    utc_dt = naive.astimezone(pytz.utc)
    utc_format = utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
    container = {                               
        "organizationId": "FOA",         
        "warehouseName": wh_code,     
        "warehousePoNumber": reference_no,  # reference_no    
        "purchaseOrderReceiptDetails": [{
            "purchaseOrderLineId": line_no,      
            "receiptDate": utc_format,        
            "warehouseSku": sku,               
            "quantity": qty
        }]
    }
    po_receipt_controller = {
        "purchaseOrderReceipts": [container]
    }
    conn = mysql_connection()
    cursor = conn.cursor()
    testing = False

    logger_q = """INSERT script_logger (response_name, response_code, status, data, response_data) VALUES (%s, %s, %s, %s, %s)"""

    if testing:
        track_sub_name = 'po_sub_test'
        po_overage_name = 'po_overage_logger_test'
        overstock_url = "https://inbound-warehouse-transaction-ws.overstock.com/purchaseOrderReceipt"
        basic = HTTPBasicAuth('furnitureofamerica', '#N5A9CmSWCoFT5do`cigE3n7J')
    else:
        track_sub_name = 'po_sub'
        po_overage_name = 'po_overage_logger'
        overstock_url = "https://api.bedbathandbeyond.com/inbound-warehouse-transaction-ws/purchaseOrderReceipt"
        basic = HTTPBasicAuth('furnitureofamerica', 'Q9fEiazCcEoX%Dt$zY3k#7#3P')

    print(po_receipt_controller)
    if testing == False:
        try:
            header = {'Content-Type': 'application/json'}
            response = requests.post(overstock_url, headers=header, json=po_receipt_controller, auth=basic)
            print("----------------------response-------------------------")
            print(response)
            print("----------------------response-------------------------")
            status = response.status_code
            if status == 200:
                cursor.execute(logger_q, ("manual_po_receipt", 200, "Success", json.dumps(po_receipt_controller, indent=4), None))
                conn.commit()
            elif status != 200 and container:
                conn.rollback()
                cursor.execute(logger_q, ("manual_po_receipt", status, "Failure", json.dumps(po_receipt_controller, indent=4), json.dumps(response.json(), indent=4)))
                conn.commit()
        except Exception as e:
            print(e)
            cursor.execute(logger_q, ("manual_po_receipt", 500, "Failure", json.dumps(po_receipt_controller, indent=4), f"{e}"))
            conn.commit()
        else:
            if status == 200 and (qty+recqty) >= ostkqty:
                # cursor.execute(f"UPDATE {track_master_name} SET received = {qty+recqty}, status = 'C', update_time = '{current_date_obj}'  WHERE master_ref_no = '{reference_no}' AND product_barcode = '{sku}'")
                cursor.execute(f"UPDATE {track_sub_name} SET received = {qty+recqty}, status = 'C', update_time = '{current_date_obj}' WHERE master_ref_no = '{reference_no}' AND product_barcode = '{sku}'")
                cursor.execute(f"UPDATE {po_overage_name} SET received_qty = {qty+recqty}, status = 'C' WHERE master_ref_no = '{reference_no}' AND product_barcode = '{sku}'")
                conn.commit()
            elif status == 200 and (qty+recqty) < ostkqty:
                # cursor.execute(f"UPDATE {track_master_name} SET received = {qty+recqty}, update_time = '{current_date_obj}'  WHERE master_ref_no = '{reference_no}' AND product_barcode = '{sku}'")
                cursor.execute(f"UPDATE {track_sub_name} SET received = {qty+recqty}, update_time = '{current_date_obj}' WHERE master_ref_no = '{reference_no}' AND product_barcode = '{sku}'")
                cursor.execute(f"UPDATE {po_overage_name} SET received_qty = {qty+recqty} WHERE master_ref_no = '{reference_no}' AND product_barcode = '{sku}'")
                conn.commit()
        finally:
            cursor.close()
            conn.close()
