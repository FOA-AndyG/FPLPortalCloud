import asyncio
import datetime
from datetime import timedelta
import re
import time

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import json
import numpy as np
import openpyxl


# Create your views here.
from Django_apps.HomeApp.functions.session_function import check_login_status, get_session_user, get_client_ip, \
    get_session_user_location
from Django_apps.OMSOrderApp.api_handler.fedex_api import *
from Django_apps.OMSOrderApp.api_handler.oms_api import createProduct, createReceivingOrder
from Django_apps.OMSOrderApp.export_function.download_attachment import get_picking_list_no_db
from Django_apps.OMSOrderApp.export_function.ils_order_import import ils_order_process_function

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
        "save_path": f"{EXCEL_FILE_PATH}/pdf_files/",
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
    username = get_session_user_username(request)
    location = get_session_user_location(request)

    # open a trailer
    if request.method == "POST" and 'trailer_confirm_btn' in request.POST:
        trailer_number = request.POST.get("trailer_number")
        create_date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

        try:
            trailer_id = create_trailer(trailer_number, username, create_date, location)
            return redirect('OMSOrderApp:web_scan_detail_page', trailer_id=trailer_id)
        except Exception as e:
            messages.warning(request, str(e))
    today_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
    open_trailers = get_trailer_data(status=0, location=location)
    # close_trailers = get_close_trailer_data(today_date)
    close_trailers = get_trailer_data(status=1, location=location, close_date=today_date)

    content = {
        "title": "FPL Web Scan Page",
        "page_head": f"Web Scan Page - {location}",
        "df_columns": ['Trailer#', 'Creator', 'Open Date', 'Close Date', 'Total Box#'],
        "open_trailers": open_trailers,
        "close_trailers": close_trailers,
        "today_date": today_date
    }
    return render(request, PAGE_PATH + "web_scan_page.html", content)


def web_scan_detail_page(request, trailer_id):
    print("web_scan_detail_page")
    if not check_login_status(request):
        return redirect("HomeApp:login")
    username = get_session_user_username(request)
    user_location = get_session_user_location(request)

    handling_types = {
        "0": "Industry Facility to 3-5 Lane",
        "1": "Diamond Bar Facility to Local",
        "2": "Tracy to NorCal",
    }

    if request.method == "POST" and 'close_btn' in request.POST:
        print("close_btn")
        dock_number = request.POST.get("dock_number")
        handling_type = request.POST.get("handling_type")
        percent_full = request.POST.get("percent_full")
        result = close_trailer(trailer_id, dock_number, handling_type, percent_full)
        if result["status"]:
            messages.success(request, f"Success: {result['message']}")
        else:
            messages.warning(request, f"Warning: {result['message']}")

        return redirect("OMSOrderApp:web_scan_page")

    # check if the trailer open;
    trailer_obj = WebScan.objects.get(id=trailer_id, status=0)
    if trailer_obj:
        content = {
            "title": trailer_obj.trailer_number,
            "trailer_number": trailer_obj.trailer_number,
            "total_box": trailer_obj.total_box,
            "username": username,
            "user_location": user_location,
            "handling_types": handling_types
        }
        return render(request, PAGE_PATH + "web_scan_detail_page.html", content)
    else:
        return redirect("OMSOrderApp:web_scan_page")


def web_scan_function(request):
    print("web_scan_function")
    username = get_session_user_username(request)
    location = get_session_user_location(request)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        trailer_number = request.POST.get("trailer_number")
        tracking_input = request.POST.get("tracking_input")
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
                save_tracking_detail_skip(trailer_number, carrier, label_tracking, username, isCheck, location)
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
        "title": "Pending order - Check",
        "page_head": "Pending order - Check",
        "display_columns": ['picking_code', 'order_code', 'order_status', 'product_barcode', 'parcel_quantity',
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

        print(rslt_df)
        if rslt_df.empty:
            messages.warning(request, "Error: No Records found.")
        else:
            messages.success(request, "Success: Records found.")

        content["display_df"] = rslt_df
    return render(request, PAGE_PATH + "web_scan_checking_page.html", content)


# working on it for printing label
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
    location = get_session_user_location(request)

    warehouse_code_map = {
        "FPL": 7,
        "TX": 11,
        "NJ": 13
    }
    wh_code = warehouse_code_map.get(location)
    import time
    if request.method == "POST" and 'compare_btn' in request.POST:
        start_time = time.time()
        result_dict = compare_web_scan_tracking_with_eccang(request, wh_code, location)
        print("--- %s seconds ---" % (time.time() - start_time))
        if result_dict["result"]:
            return result_dict["response"]
        else:
            messages.warning(request, result_dict["msg"])

    if request.method == "POST" and 'compare2_btn' in request.POST:
        start_time = time.time()
        result_dict = compare_web_scan_tracking_with_eccang_pending_orders(request, wh_code, location)
        print("--- %s seconds ---" % (time.time() - start_time))
        if result_dict["result"]:
            return result_dict["response"]
        else:
            messages.warning(request, result_dict["msg"])
    content = {
        "title": "Web Scan Report",
        "page_head": f"Scan Report - {location}",
        "df_title": "Web Scan Table",
        "df_columns": ['ContainerNo', 'Carrier', 'Tracking', 'CreateDate'],
        "display_columns": ['ContainerNo', 'Carrier', 'Tracking', 'CreateDate', 'MachineName',
                            "OrderCode", "ProductCode"],
    }

    # get picking list table
    picking_df = get_picking_list_no_db(wh_code)
    if not picking_df.empty:
        content["picking_list"] = picking_df["picking_code"].tolist()

    from datetime import datetime, timedelta
    over_all_list = []
    for i in range(7):
        over_all_list.append(datetime.strftime(datetime.now() + timedelta(days=-i), '%y%m%d'))
    content["overall_picking_list"] = over_all_list

    content["display_data"] = get_tracking_detail_data(5000, location)

    if request.method == "POST" and 'search_btn' in request.POST:
        search_select = request.POST.get('search_select')
        search_input = request.POST.get('search_input')
        content["display_data"] = search_tracking_detail_data(search_select, search_input)

    return render(request, PAGE_PATH + "web_scan_report.html", content)


# Andy add: 03/17/2024
def fpl_ils_order_process(request):
    print("fpl_ils_order_process")
    if not check_login_status(request):
        return redirect("HomeApp:login")

    content = {
        "title": "FPL & ILS Order Process",
        "page_head": "FPL & ILS Order Process",
    }

    if request.method == "POST" and 'import_button' in request.POST:
        print("import_btn")
        result_dict = ils_order_process_function(request)
        if result_dict["result"]:
            return result_dict["response"]
        else:
            messages.warning(request, result_dict["msg"])

    return render(request, PAGE_PATH + "fpl_ils_order_process.html", content)


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


def fedex_tracking_status_checking(request):
    print("fedex_tracking_status_checking")
    content = {
        "title": "FedEX Tracking Status",
        "page_head": "FedEX Tracking Status",
    }

    if not check_login_status(request):
        return redirect("HomeApp:login")

    if request.method == "POST" and 'import_button' in request.POST:
        print("import_button clicked")
        start_time = time.time()
        #  1. get excel file from user upload
        excel_file = request.FILES.get('vc_excel')
        try:
            print("# 2. Reading the excel file using Pandas")
            df = pd.read_excel(excel_file)

            print("# 3. Checking if the '跟踪号' column exists")
            if '跟踪号' not in df.columns:
                messages.warning(request, "Excel file does not contain '跟踪号' column.")
            else:
                df['跟踪号'] = df['跟踪号'].astype(str)
                print("# 4. Check for errors and print messages including row index")
                df['tracking_valid'] = df['跟踪号'].apply(lambda x: 1 if is_valid_fedex_tracking_number(x) else 0)
                errors = df[df['tracking_valid'] == 0]
                if not errors.empty:
                    messages.warning(request, "Error: Invalid tracking numbers found:")
                    for index, row in errors.iterrows():
                        messages.warning(request, f"Row ID: {index} - Invalid Tracking Number: {row['跟踪号']}")
                else:
                    print("# 5. get fedex api to check tracking number")
                    fedex_api = FedExTrackingApp(False)
                    fedex_token_response = fedex_api.get_access_token()
                    if fedex_token_response["success"]:
                        api_token = fedex_token_response["msg"]

                        print("# 6. Iterate over the DataFrame and print the tracking numbers")
                        df['tracking_status'] = df['跟踪号'].apply(lambda x: fedex_api.get_fedex_status(api_token, x))
                        # After getting tracking status
                        df['status'] = df['tracking_status'].apply(lambda x: x['status'] if isinstance(x, dict) else x)
                        df['service'] = df['tracking_status'].apply(
                            lambda x: x.get('service', '') if isinstance(x, dict) else '')
                        df['ship_date'] = df['tracking_status'].apply(
                            lambda x: x['dates'].get('ship_date') if isinstance(x, dict) else None)
                        df['pickup_date'] = df['tracking_status'].apply(
                            lambda x: x['dates'].get('pickup_date') if isinstance(x, dict) else None)
                        df['actual_delivery'] = df['tracking_status'].apply(
                            lambda x: x['dates'].get('actual_delivery') if isinstance(x, dict) else None)
                        df['estimated_delivery'] = df['tracking_status'].apply(
                            lambda x: x['dates'].get('estimated_delivery') if isinstance(x, dict) else None)

                        # # For the events timeline, you might want to join them with newlines
                        # df['transit_timeline'] = df['tracking_status'].apply(
                        #     lambda x: "\n".join([f"{e['date']} - {e['description']} ({e['location']})"
                        #                          for e in x['dates'].get('all_events', [])])
                        #     if isinstance(x, dict) else None
                        # )

                        current_dt = datetime.now()
                        df['estimated_delivery_date'] = df['estimated_delivery'].apply(
                            lambda x: x[:10] if pd.notna(x) else None
                        )
                        df['estimated_delivery_dt'] = pd.to_datetime(df['estimated_delivery_date'], errors='coerce')

                        df['late_alert'] = (
                                df['estimated_delivery_dt'].notna() &  # Only check rows with valid dates
                                (df['status'] != 'Delivered') &  # Skip delivered packages
                                (df['status'] != 'No tracking information') &  # Skip invalid tracking
                                (current_dt > (df['estimated_delivery_dt'] + timedelta(days=3)))  # 3-day check
                        )

                        df = df.drop(columns=['tracking_valid', 'tracking_status', 'estimated_delivery_dt'], errors='ignore')

                        print("# 7. download the new excel file.")
                        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                        response['Content-Disposition'] = f"attachment; filename=tracking_status_result.xlsx"
                        df.to_excel(response, index=False)
                        end_time = time.time()
                        duration = end_time - start_time
                        messages.success(request, f"Success: Tracking status result excel file has been downloaded. "
                                                  f"The function took {duration} seconds to complete.")
                        response.set_cookie('fileDownload', 'true', max_age=1200)  # Set cookie, expire in 10 minutes
                        return response
                    else:
                        messages.warning(request, f"Error: {fedex_token_response['msg']}")
        except Exception as e:
            messages.warning(request, f"Error processing file: {e}")

    return render(request, PAGE_PATH + "fedex_tracking_status_checking.html", content)


def ecang_order_dashboard_page(request):
    print("ecang_order_dashboard_page")
    if not check_login_status(request):
        return redirect("HomeApp:login")

    content = {
        "title": "Order Dashboard",
        "page_head": "Order Dashboard",
    }
    try:
        recent_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
        with ECANGMySQLConnection() as db:
            sql = f"""
                SELECT o.order_code
                    , o.order_status
                    , o.sm_code
                    , o.parcel_quantity
                    , s.tracking_number
                    , o.update_time
                    , o.remark
                FROM orders o
                LEFT JOIN ship_order s ON o.order_id=s.order_id
                WHERE o.warehouse_id = 7
                    AND o.order_status IN (5,6,7)
                    AND o.update_time > "{recent_date}"
                """
            df = db.read_sql_to_dataframe(sql)
            df['tracking_number'] = df['tracking_number'].astype(str)
            df["tracking_number"] = df["tracking_number"].str.replace(' ', '')

            # Calculate statistics
            small_parcel_df = df[df['parcel_quantity'] == 1]
            ltl_order_df = df[df['parcel_quantity'] > 1]

            small_parcel_total_orders = len(small_parcel_df)
            small_parcel_total_quantity = small_parcel_df['parcel_quantity'].sum()

            ltl_order_total_orders = len(ltl_order_df)
            ltl_order_total_quantity = ltl_order_df['parcel_quantity'].sum()

            # UPS Orders
            ups_df = small_parcel_df[
                (small_parcel_df['sm_code'].str.contains("UPS")) |
                ((small_parcel_df['sm_code'] == "FDW_NO_LABEL") & small_parcel_df['tracking_number'].str.startswith(
                    "1Z"))
                ]
            ups_total_orders = len(ups_df)
            ups_total_quantity = ups_df['parcel_quantity'].sum()

            # FEDEX Orders
            fedex_df = small_parcel_df[
                (small_parcel_df['sm_code'].str.contains("FEDEX")) |
                ((small_parcel_df['sm_code'] == "FDW_NO_LABEL") & small_parcel_df['tracking_number'].str.len() == 12)
                ]
            fedex_total_orders = len(fedex_df)
            fedex_total_quantity = fedex_df['parcel_quantity'].sum()

            content.update({
                "small_parcel_total_orders": small_parcel_total_orders,
                "small_parcel_total_quantity": small_parcel_total_quantity,
                "ltl_order_total_orders": ltl_order_total_orders,
                "ltl_order_total_quantity": ltl_order_total_quantity,
                "ups_total_orders": ups_total_orders,
                "ups_total_quantity": ups_total_quantity,
                "fedex_total_orders": fedex_total_orders,
                "fedex_total_quantity": fedex_total_quantity,
                "other_order_quantity": small_parcel_total_quantity-fedex_total_orders-ups_total_quantity,
                "current_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
    except Exception as e:
        print(e)
        messages.warning(request, f"Error: {e}")
        content.update({
            "small_parcel_total_orders": 0,
            "small_parcel_total_quantity": 0,
            "ltl_order_total_orders": 0,
            "ltl_order_total_quantity": 0,
            "ups_total_orders": 0,
            "ups_total_quantity": 0,
            "fedex_total_orders": 0,
            "fedex_total_quantity": 0,
            "other_order_quantity": 0,
            "current_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    return render(request, PAGE_PATH + "ecang_order_dashboard_page.html", content)


def oms_receiving_order_and_product(request):
    print("create_oms_receiving_order_and_product")
    if not check_login_status(request):
        return redirect("HomeApp:login")
    content = {
        "title": "CFSFPL1 Receiving Order and Product",
        "page_head": "CFSFPL1 Receiving Order and Product",
    }

    if request.method == "POST":
        # Handle the Download Template button
        if "download_button" in request.POST:
            # Create Excel template
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Template"
            ws.append(["PONumber", "ContainerNo", "Item", "BarCode"])  # Add your required columns here

            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = "attachment; filename=template.xlsx"
            wb.save(response)
            return response
        elif "import_button" in request.POST and "import_file_path" in request.FILES:
            # Process uploaded file
            uploaded_file = request.FILES["import_file_path"]
            # Read the file into a dataframe
            try:
                df = pd.read_excel(uploaded_file)
                # if df is not empty, then call createProduct(df)
                if not df.empty:
                    fptest_api_key = {
                        "appToken": "f88b7a4b18ebe887ee7b3f5af1e1b8d5",
                        "appKey": "39c64b08d11e7f2dcabdead6aa461a2f",
                    }
                    CFSFPL1_API_KEY = {
                        "appToken": "a1de6047ef2f8cd059299db0890fb26b",
                        "appKey": "05575f447d19c8f547c9413a186f6973",
                    }
                    result = createProduct(df, CFSFPL1_API_KEY)
                    if result['status'] == "success":
                        # Call createReceivingOrder(df)
                        rv_order_result = createReceivingOrder(df, CFSFPL1_API_KEY)
                        if rv_order_result['status'] == "success":
                            messages.success(request, rv_order_result['message'])
                        else:
                            messages.warning(request, rv_order_result['message'])
                    else:
                        messages.warning(request, result['message'])
            except Exception as e:
                messages.warning(request, f"Error: {e}")

    return render(request, PAGE_PATH + "oms_receiving_order_and_product.html", content)



