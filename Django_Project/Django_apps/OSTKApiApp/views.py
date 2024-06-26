from http.client import HTTPResponse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
import pandas as pd
from .functions.ostk_inventory import tx_ostk_inv, lax_ostk_inv
from .functions import ostk_orders
from .functions import ostk_functions
from .functions import ostk_po
from Django_apps.OSTKApiApp.functions.sql_connection import *

PAGE_PATH = "OSTKApiApp/pages/"
# Create your views here.

def ostk_inventory(request):
    conn = wms_mysql_connection()
    data_tx = tx_ostk_inv(conn)
    data_lax = lax_ostk_inv(conn)
    content = {
        "data": data_tx,
        "data_lax": data_lax
    }
    conn.close()
    # return render(request, "programtools/pages/ostk_inventory.html", {"content": content})
    return render(request, PAGE_PATH + "ostk_inventory.html", {"content": content})

def tx_ostk_orders(request):
    conn = mysql_connection()
    conn_wms = wms_mysql_connection()
    conn_cloud = cloud_connection()

    if request.method == 'GET' and 'export' in request.GET:
        export = ostk_orders.tx_ostk_export(conn, conn_wms, conn_cloud)
        conn.close()
        conn_wms.close()
        conn_cloud.close()
        return export
    
    # need to include other branches
    shipconfirm = ostk_orders.tx_ostk_shipconfirm(conn, conn_wms, conn_cloud)
    open = ostk_orders.tx_ostk_open(conn, conn_wms, conn_cloud)
    error = ostk_orders.tx_ostk_error(conn, conn_wms, conn_cloud)

    content = {
        "open": open,
        "error": error,
        "shipconfirm": shipconfirm
    }

    conn.close()
    conn_wms.close()
    conn_cloud.close()
    return render(request, PAGE_PATH + "tx_ostk_orders.html", {"content": content})

def lax_ostk_orders(request):
    conn = mysql_connection()
    conn_wms = wms_mysql_connection()
    conn_cloud = cloud_connection()

    if request.method == 'GET' and 'export' in request.GET:
        export = ostk_orders.lax_ostk_export(conn, conn_wms, conn_cloud)
        conn.close()
        conn_wms.close()
        conn_cloud.close()
        return export
    
    # need to include other branches
    shipconfirm = ostk_orders.lax_ostk_shipconfirm(conn, conn_wms, conn_cloud)
    open = ostk_orders.lax_ostk_open(conn, conn_wms, conn_cloud)
    error = ostk_orders.lax_ostk_error(conn, conn_wms, conn_cloud)
    content = {
        "open": open,
        "error": error,
        "shipconfirm": shipconfirm
    }

    conn.close()
    conn_wms.close()
    conn_cloud.close()
    return render(request, PAGE_PATH + "lax_ostk_orders.html", {"content": content})


def ostk_adj(request):
    print("ostk_adj")

    if request.method == 'GET' and 'item' in request.GET:
        id = int(request.GET.get('id'))
        wh = int(request.GET.get('wh'))
        item = request.GET.get('item')
        qty = int(request.GET.get('qty'))
        reason_code = request.GET.get('reason_code')
        status = ostk_functions.create(request, id, wh, item, qty, reason_code)
        return JsonResponse({"status": status}, safe=False)

    adj_data = ostk_functions.get_today_adjustments()
    history = ostk_functions.get_adj_history()
    
    content = {
        "adj_data": adj_data,
        "history": history
        # "order_codes": order_code
    }
    return render(request, PAGE_PATH + "ostk_adj.html", content)


def ostk_po_import(request):
    print("ostk_po_import")
    if request.method == 'POST' and 'import_button' in request.POST:
        upload = request.FILES['import_file_path']
        ostk_po_db = pd.read_excel(upload, engine='openpyxl', skiprows=1)
        ostk_functions.import_ostk_po_func(request, ostk_po_db)
        return render(request, PAGE_PATH + "ostk_po_import.html")
    return render(request, PAGE_PATH + "ostk_po_import.html")


def ostk_upc_export(request):
    print("ostk_upc_export")
    if request.method == 'GET' and 'upc_export' in request.GET:
        print("ajax")
        export = ostk_functions.ostk_upc_export(request)
        return export
    return render(request, PAGE_PATH + "ostk_upc_export.html")

def ostk_sh(request):
    print("ostk sh")

    if request.method == 'POST' and 'shortship' in request.POST:
        ostk_functions.manual_shortship(request)
        return redirect("OSTKApiApp:ostk_sh")

    if request.method == 'GET' and 'ref' in request.GET:
        print("ajax")
        ref = request.GET.get('ref')
        o_codes = ostk_functions.get_order_codes_by_ref(ref)
        return JsonResponse({"o_codes": o_codes, "ref": ref}, safe=False)

    order_code = ostk_functions.get_order_codes()
    content = {
        "order_codes": order_code
    }
    return render(request, PAGE_PATH + "ostk_sh.html", content)


def ostk_po_receipt(request):
    conn = mysql_connection()
    print("po_receipt")
    po_data = ostk_po.get_ostk_po(conn)
    content = {
        "po_data": po_data
    }
    conn.close()
    return render(request, PAGE_PATH + "ostk_po_receipt.html", content)

def ostk_po_receipt_popup(request, receiving_code):
    print("po_receipt_popup")
    conn = mysql_connection()
    view_data, view_size = ostk_po.get_po_view(conn, receiving_code)
    content = {
        "rc": receiving_code,
        "view_data": view_data,
        "view_size": view_size
    }
    conn.close()
    return render(request, PAGE_PATH + "ostk_po_receipt_popout.html", content)

def ostk_po_receipt_popup_ref(request, master_ref_no):
    print("po_receipt_popup_ref")
    conn = mysql_connection()
    view_data, view_size = ostk_po.get_ref_view(conn, master_ref_no)
    content = {
        "mr": master_ref_no,
        "view_data": view_data,
        "view_size": view_size
    }
    conn.close()
    return render(request, PAGE_PATH + "ostk_po_receipt_popout_ref.html", content)

def ostk_overages(request):
    if request.method == 'POST' and 'send_overage' in request.POST:
        print("overage")
        ostk_functions.manual_overage(request)
        return redirect("OSTKApiApp:ostk_overages")
    
    if request.method == 'GET' and 'pass_overage' in request.GET:
        return JsonResponse(None)
    
    overage_data, overage_size = ostk_functions.get_overages()
    content = {
        "overage_data": overage_data,
        "overage_size": overage_size
    }
    return render(request, PAGE_PATH + "ostk_overages.html", content)