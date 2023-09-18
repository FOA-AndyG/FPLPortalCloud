import asyncio
import datetime

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import json

# Create your views here.
from Django_apps.HomeApp.functions.session_function import check_login_status, get_session_user, get_client_ip
from Django_apps.OMSOrderApp.export_function.download_attachment import get_picking_list_no_db

from Django_apps.OMSOrderApp.picking_functions.scan_support_functions import *
from Django_apps.OMSOrderApp.reports.direct_sale_pricing_functions import *
from Django_apps.OMSOrderApp.reports.scan_function import *

PAGE_PATH = "OMSOrderApp/pages/"


def dashboard(request):
    # todo: need to working on OMSOrderApp dashboard page
    print("dashboard page")
    if not check_login_status(request):
        return redirect("HomeApp:login")
    content = {
        "title": "Dashboard Page",
    }
    ip = get_client_ip(request)
    print(ip)
    user = get_session_user(request)
    print(user.fullname)

    return render(request, PAGE_PATH + "dashboard.html", content)


def pdf_merge_page(request):
    print("pdf_merge_page")
    if not check_login_status(request):
        return redirect("HomeApp:login")

    content = {
        "title": "Download Order Attachment Page",
        "save_path": "static/OMSOrderApp/pdf_files/",
        "download_path": "",
        "result_msg": ""
    }

    if request.method == "POST" and 'merge_btn' in request.POST:
        from PyPDF2 import PdfFileMerger
        from datetime import datetime
        import os

        merger = PdfFileMerger()
        for pdf in request.FILES.getlist('upload'):
            # print(pdf)
            merger.append(pdf, import_bookmarks=False)

        if not os.path.exists(content["save_path"]):
            os.makedirs(content["save_path"], 777)

        current_time = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
        merger.write(content["save_path"] + "pdf" + current_time + ".pdf")
        merger.close()
        content["download_path"] = "OMSOrderApp/pdf_files/" + "pdf" + current_time + ".pdf"
        content["result_msg"] = "Success: Please click the button to download."

    return render(request, PAGE_PATH + "pdf_merge_page.html", content)


# Andy: updated: 08/07/2022
def web_scan_page(request):
    print("web_scan_page")
    if not check_login_status(request):
        return redirect("HomeApp:login")

    # open a trailer
    if request.method == "POST" and 'trailer_confirm_btn' in request.POST:
        trailer_number = request.POST.get("trailer_number")
        username = get_session_user_username(request)
        create_date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

        try:
            create_trailer(trailer_number, username, create_date)
            return redirect('OMSOrderApp:web_scan_detail_page', trailer_number=trailer_number)
        except Exception as e:
            messages.warning(request, str(e))
    today_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
    open_trailers = get_trailer_data(status=0)
    close_trailers = get_close_trailer_data(today_date)
    content = {
        "title": "FPL Web Scan Page",
        "page_head": "FPL Web Scan Page",
        "df_columns": ['Trailer#', 'Creator', 'Open Date', 'Close Date', 'Total Box#'],
        "open_trailers": open_trailers,
        "close_trailers": close_trailers,
        "today_date": today_date
    }
    return render(request, PAGE_PATH + "web_scan_page.html", content)


def web_scan_detail_page(request, trailer_number):
    print("web_scan_detail_page")
    if not check_login_status(request):
        return redirect("HomeApp:login")

    if request.method == "POST" and 'close_btn' in request.POST:
        print("close_btn")
        close_trailer(trailer_number)
        return redirect("OMSOrderApp:web_scan_page")

    # check if the trailer open;
    trailer_obj_list = get_trailer_data(trailer_number=trailer_number, status=0)
    if trailer_obj_list.first():
        content = {
            "title": trailer_number,
            "trailer_number": trailer_number,
            "total_box": trailer_obj_list.first().total_box,
            "username": get_session_user_username(request)
        }
        return render(request, PAGE_PATH + "web_scan_detail_page.html", content)
    else:
        return redirect("OMSOrderApp:web_scan_page")


def web_scan_function(request):
    print("web_scan_function")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        trailer_number = request.POST.get("trailer_number")
        tracking_input = request.POST.get("tracking_input")
        username = request.POST.get("username")
        isCheck = request.POST.get("isCheck")
        print(username, trailer_number, tracking_input, isCheck)

        # check scan_tracking if it's valid
        check_carrier = {
            "1Z": "UPS",
            "96": "FEDEX",
            "42": "USPS",  # 420770189305510923030833722030
            "10": "FEDEX",  # FedEx next day
            "FO": "WH03",
            "TB": "AMXL",
            "D1": "ONTRACK"
        }
        label_tracking = ""
        carrier = check_carrier.get(tracking_input[:2])
        if carrier:
            if carrier == "FEDEX" or carrier == "USPS":
                label_tracking = tracking_input[-12:]
            else:
                label_tracking = tracking_input
        else:
            carrier = "Unknown"

        print("carrier:", carrier)
        if carrier not in trailer_number:
            content = {
                "result": False,
                "message": f"Error: loading wrong box into the trailer"
            }
            return JsonResponse(content)
        else:
            # TODO: check if the tracking exists in internal database
            is_pass_check = check_exist_tracking(trailer_number, label_tracking)
            if is_pass_check:
                print("save scan record")
                # skip check with Ecang orders
                save_tracking_detail_skip(trailer_number, carrier, label_tracking, username, isCheck)
                content = {
                    "result": True,
                    "message": f"Success: {label_tracking}"
                }
            else:
                save_tracking_detail_error(trailer_number, carrier, label_tracking, username, isCheck,
                                           "Error: Tracking# already scanned")
                content = {
                    "username": username,
                    "create_date": datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
                    "result": False,
                    "message": f"Error: {label_tracking} - Tracking# already scanned"
                }
            return JsonResponse(content)


def web_scan_wrong_tracking_page(request):
    return render(request, PAGE_PATH + "web_scan_wrong_tracking_page.html")


def web_scan_checking_page(request):
    print("web_scan_checking_page")

    content = {
        "title": "Tracking Check",
        "page_head": "Tracking Check",
        "display_columns": ['picking_code', 'order_code', 'product_barcode', 'parcel_quantity',
                            'tracking_number', 'multiple_tracking_number'],
    }

    if request.method == "POST" and "tracking_submit" in request.POST:
        select_input = request.POST.get("select_input")
        tracking_input = request.POST.get("tracking_input")
        ecang_data_df = get_eccang_order_data()

        if select_input == "Tracking":
            rslt_df = ecang_data_df[ecang_data_df['tracking_number'].str.contains(tracking_input)]
            if rslt_df.empty:
                rslt_df = ecang_data_df[ecang_data_df['multiple_tracking_number'].str.contains(tracking_input)]
        elif select_input == "Picking":
            rslt_df = ecang_data_df[ecang_data_df['picking_code'].str.contains(tracking_input)]
        else:
            rslt_df = ecang_data_df[ecang_data_df['product_barcode'].str.contains(tracking_input)]

        if rslt_df.empty:
             messages.warning(request, "Error: No Records found.")
        else:
            messages.success(request, "Success: Records found.")

        content["display_df"] = rslt_df
    return render(request, PAGE_PATH + "web_scan_checking_page.html", content)


def web_scan_printing_page(request):
    print("web_scan_printing_page")
    if request.method == "POST" and "picking_submit" in request.POST:
        picking_input = request.POST.get("picking_input")

    content = {
        "title": "Label Print",
        "page_head": "Label Print",
    }
    return render(request, PAGE_PATH + "web_scan_printing_page.html", content)


# Andy add: 08/17/2022
def web_scan_report(request):
    print("web_scan_report")
    if not check_login_status(request):
        return redirect("HomeApp:login")

    import time
    if request.method == "POST" and 'compare_btn' in request.POST:
        start_time = time.time()
        result_dict = compare_web_scan_tracking_with_eccang(request)
        print("--- %s seconds ---" % (time.time() - start_time))
        if result_dict["result"]:
            return result_dict["response"]
        else:
            messages.warning(request, result_dict["msg"])

    if request.method == "POST" and 'compare2_btn' in request.POST:
        start_time = time.time()
        result_dict = compare_web_scan_tracking_with_eccang_pending_orders(request, 7)
        print("--- %s seconds ---" % (time.time() - start_time))
        if result_dict["result"]:
            return result_dict["response"]
        else:
            messages.warning(request, result_dict["msg"])

    if request.method == "POST" and 'export_btn_wh3' in request.POST:
        start_time = time.time()
        result_dict = compare_web_scan_tracking_with_eccang_pending_orders(request, 8)
        print("--- %s seconds ---" % (time.time() - start_time))
        if result_dict["result"]:
            return result_dict["response"]
        else:
            messages.warning(request, result_dict["msg"])

    content = {
        "title": "Web Scan Report",
        "page_head": "Scan Report",
        "df_title": "Web Scan Table",
        "df_columns": ['ContainerNo', 'Carrier', 'Tracking', 'CreateDate'],
        "display_columns": ['ContainerNo', 'Carrier', 'Tracking', 'CreateDate', 'MachineName',
                            "OrderCode", "ProductCode"],
    }

    # # get picking list table
    # picking_df = get_picking_list_no_db(7)
    # if not picking_df.empty:
    #     content["picking_list"] = picking_df["picking_code"].tolist()
    #
    # # get WH3 picking list table
    # picking_df = get_picking_list_no_db(8)
    # if not picking_df.empty:
    #     content["picking_list_wh3"] = picking_df["picking_code"].tolist()
    #
    # from datetime import datetime, timedelta
    # over_all_list = []
    # for i in range(7):
    #     over_all_list.append(datetime.strftime(datetime.now() + timedelta(days=-i), '%y%m%d'))
    # content["overall_picking_list"] = over_all_list

    content["display_data"] = get_tracking_detail_data(5000)

    return render(request, PAGE_PATH + "web_scan_report.html", content)


# Andy: test picking function
def picking_page(request):
    print("picking_page")
    if not check_login_status(request):
        return redirect("HomeApp:login")

    user_name = get_session_user_username(request)
    content = {
        "title": "Picking",
        "username": user_name,
        "df_columns": ['ContainerNo', 'Carrier', 'Tracking', 'CreateDate'],
        "display_columns": ['ContainerNo', 'Carrier', 'Tracking', 'CreateDate', 'MachineName',
                            "OrderCode", "ProductCode"],
    }
    picking_df = get_picking_list_no_db(7)
    if not picking_df.empty:
        content["picking_list"] = picking_df["picking_code"].tolist()

    # let picker to register the picking list

    # show current_pending_picking_list with current progress

    return render(request, PAGE_PATH + "picking_page.html", content)
