import os
from datetime import datetime

from django.db.models.query_utils import Q
import pandas as pd
from django.db.models import F
from django.http import HttpResponse

from Database.mysql_handler import ECANGMySQLConnection, SQLAlchemyHandler
from Django_Project.settings import EXCEL_FILE_PATH
from Django_apps.OMSOrderApp.export_function.download_attachment import get_picking_list
from Django_apps.OMSOrderApp.models import WebScan, WebScanDetail, WebScanDetailError
from Django_apps.OMSOrderApp.reports.scan_function import return_match_tracking_function, \
    return_match_tracking_function_no_shipped_orders


def create_trailer(trailer_number, username, create_date, location):
    obj = WebScan(trailer_number=trailer_number, username=username, create_date=create_date,
                  total_box=0, status=0, location=location, send_email=0)
    obj.save()
    return obj.id


def close_trailer(trailer_id, dock_number, handling_type, percent_full):
    try:
        obj = WebScan.objects.get(id=trailer_id, status=0)
        obj.close_date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        obj.status = 1

        detail_total_count = WebScanDetail.objects.filter(trailer_number=obj.trailer_number, check_system=0).count()
        obj.total_box = detail_total_count
        # WebScanDetail.objects.filter(trailer_number=trailer_number, check_system=0).update(check_system=1)

        if "FEDEX" in obj.trailer_number and obj.location == 'FPL':
            print("Start to send email to FedEx...")
            handling_types = {
                "0": "Industry Facility to 3-5 Lane",
                "1": "Diamond Bar Facility to Local",
                "2": "Tracy to NorCal",
            }
            zone = handling_types.get(handling_type, "Unknown")
            obj.dock_number = dock_number
            obj.percent_full = percent_full
            obj.zone = zone
            obj.save()
            return {"status": True, "message": f"Trailer {obj.trailer_number} closed successfully."}
        else:
            obj.save()
            return {"status": True, "message": f"Trailer {obj.trailer_number} closed successfully."}
    except Exception as e:
        print(f"Error closing trailer: {e}")
        return {"status": False, "message": f"Error closing trailer: {e}"}


def get_trailer_data(**kwargs):
    qq = Q()
    for key, value in kwargs.items():
        qq.add(Q(**{"%s__icontains" % key: value}), Q.AND)

    obj = WebScan.objects.filter(qq).order_by('-create_date')

    return obj


def get_close_trailer_data(today_date):
    obj = WebScan.objects.filter(status=1, close_date__gte=today_date).order_by('-close_date')
    return obj


def check_exist_tracking(trailer_number, tracking_number):
    obj = WebScanDetail.objects.filter(trailer_number=trailer_number, tracking_number=tracking_number)
    if not obj:
        return True
    else:
        return False


def save_tracking_detail(trailer_number, carrier, tracking_number, username, order_code, product_code, check_system):
    obj = WebScanDetail(trailer_number=trailer_number, carrier=carrier,
                        tracking_number=tracking_number, username=username,
                        create_date=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
                        order_code=order_code, product_code=product_code, check_system=check_system)
    obj.save()


def save_tracking_detail_skip(trailer_number, carrier, tracking_number, username, check_system, location):
    obj = WebScanDetail(trailer_number=trailer_number, carrier=carrier,
                        tracking_number=tracking_number, username=username,
                        create_date=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
                        check_system=check_system, location=location)
    obj.save()

    WebScan.objects.filter(trailer_number=trailer_number, status=0).update(total_box=F('total_box') + 1)


def save_tracking_detail_error(trailer_number, carrier, tracking_number, username, check_system, note):
    obj = WebScanDetailError(trailer_number=trailer_number, carrier=carrier,
                             tracking_number=tracking_number, username=username,
                             create_date=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
                             check_system=check_system, note=note)
    obj.save()


def get_tracking_detail_data(total_number, location):
    obj = WebScanDetail.objects.filter(location=location).order_by('-create_date')[:total_number]
    return obj


def search_tracking_detail_data(search_select, search_input):
    if search_select == "ContainerNo":
        obj = WebScanDetail.objects.filter(trailer_number=search_input)
    else:
        obj = WebScanDetail.objects.filter(tracking_number=search_input)
    return obj


def get_eccang_order_data():
    try:
        with ECANGMySQLConnection() as db:
            sql = """
            SELECT o.order_code
            , o.order_status
            , p.product_barcode
            , o.parcel_quantity
            , s.tracking_number
            , oa.multiple_tracking_number
            , p.picking_code
            from orders o
            LEFT JOIN picking_detail AS p ON o.order_id = p.order_id
            LEFT JOIN ship_order s ON o.order_id=s.order_id
            LEFT JOIN order_additional AS oa ON o.order_id = oa.order_id
            WHERE o.warehouse_id in (7,8)
            AND o.order_status IN (5,6,7)
            """
            df = db.read_sql_to_dataframe(sql)
            df['tracking_number'] = df['tracking_number'].astype(str)
            df["tracking_number"] = df["tracking_number"].str.replace(' ', '')
            # print(df.head(5))
    except Exception as e:
        print(e)
        df = pd.DataFrame()
    return df


def compare_web_scan_tracking_with_eccang(request, warehouse_code, location):
    scan_df = pd.DataFrame(list(get_tracking_detail_data(20000, location).values()))
    scan_df = scan_df.rename(columns={"tracking_number": "Tracking", "carrier": "Carrier"})
    scan_df = scan_df.drop(columns=['id', 'check_system', 'order_code', 'product_code'])

    picking = request.POST.get("search_list")
    with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                           password="A!05FOA2021edi") as db:
        if "PL" not in picking:
            final_df = pd.DataFrame()
            picking_df = get_picking_list(db, warehouse_code)
            new_picking_list = picking_df["picking_code"].tolist()
            first = 0
            for p in new_picking_list:
                # if p != "PL72206030007":
                if picking in p:
                    print(p)
                    if first == 0:
                        final_df = return_match_tracking_function(db, p, scan_df)
                        first += 1
                    else:
                        final_df = final_df.append(return_match_tracking_function(db, p, scan_df), ignore_index=True)
        else:
            final_df = return_match_tracking_function(db, picking, scan_df)

    if not final_df.empty:
        file_path = f"{EXCEL_FILE_PATH}/report_files/tracking_report/{picking}/"
        if not os.path.exists(file_path):
            os.makedirs(file_path, 777)
        current_time = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
        download_path = f"{file_path}{picking}_tracking_report_{current_time}.xlsx"

        final_df.to_excel(download_path, index=False)
        # final_df.to_excel(download_path)

        excel = open(download_path, "rb")
        response = HttpResponse(excel,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={picking}_tracking_report_{current_time}.xlsx'

        content = {
            "result": True,
            "df": final_df,
            "download_path": download_path,
            "response": response,
            "msg": "Success"
        }
    else:
        content = {
            "result": False,
            "msg": "No picking info"
        }
    return content


def compare_web_scan_tracking_with_eccang_pending_orders(request, warehouse_code, location):
    scan_df = pd.DataFrame(list(get_tracking_detail_data(20000, location).values()))
    scan_df = scan_df.rename(columns={"tracking_number": "Tracking", "carrier": "Carrier"})
    scan_df = scan_df.drop(columns=['id', 'check_system', 'order_code', 'product_code'])

    picking = request.POST.get("search_list")
    with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                           password="A!05FOA2021edi") as db:
        if "PL" not in picking:
            final_df = pd.DataFrame()
            picking_df = get_picking_list(db, warehouse_code)
            new_picking_list = picking_df["picking_code"].tolist()
            first = 0
            for p in new_picking_list:
                if picking in p:
                    print(p)
                    if first == 0:
                        final_df = return_match_tracking_function_no_shipped_orders(db, p, scan_df)
                        first += 1
                    else:
                        final_df = final_df.append(return_match_tracking_function_no_shipped_orders(db, p, scan_df), ignore_index=True)
        else:
            final_df = return_match_tracking_function_no_shipped_orders(db, picking, scan_df)

    if not final_df.empty:
        file_path = f"{EXCEL_FILE_PATH}/report_files/tracking_report/{picking}/"
        if not os.path.exists(file_path):
            os.makedirs(file_path, 777)
        current_time = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
        download_path = f"{file_path}{picking}_tracking_report_{current_time}.xlsx"

        final_df.to_excel(download_path, index=False)
        # final_df.to_excel(download_path)

        excel = open(download_path, "rb")
        response = HttpResponse(excel,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={picking}_tracking_report_{current_time}.xlsx'

        content = {
            "result": True,
            "df": final_df,
            "download_path": download_path,
            "response": response,
            "msg": "Success"
        }
    else:
        content = {
            "result": False,
            "msg": "No picking info"
        }
    return content


def check_wms_sku():
    try:
        with ECANGMySQLConnection() as db:
            sql = """
            SELECT o.order_code
            , o.order_status
            , p.product_barcode
            , o.parcel_quantity
            , s.tracking_number
            , oa.multiple_tracking_number
            , p.picking_code
            from orders o
            LEFT JOIN picking_detail AS p ON o.order_id = p.order_id
            LEFT JOIN ship_order s ON o.order_id=s.order_id
            LEFT JOIN order_additional AS oa ON o.order_id = oa.order_id
            WHERE o.warehouse_id in (7,8)
            AND o.order_status IN (5,6,7)
            """
            df = db.read_sql_to_dataframe(sql)
            df['tracking_number'] = df['tracking_number'].astype(str)
            df["tracking_number"] = df["tracking_number"].str.replace(' ', '')
            # print(df.head(5))
    except Exception as e:
        print(e)
        df = pd.DataFrame()
    return df


# get sellable, reserved, onway product dimension from wms.product_inventory
def get_wms_product_dimension():
    try:
        with ECANGMySQLConnection() as db:
            sql = """
            SELECT 
                inv.customer_code, 
                inv.product_id, 
                inv.product_barcode AS SKU, 
                inv.pi_sellable, 
                inv.pi_reserved, 
                inv.pi_onway,
                COALESCE(p.product_length, pa.product_length) AS length,
                COALESCE(p.product_width, pa.product_width) AS width,
                COALESCE(p.product_height, pa.product_height) AS height
            FROM wms.product_inventory as inv 
            LEFT JOIN wms.product_warehouse_attribute AS p ON inv.product_id = p.product_id
            LEFT JOIN wms.product AS pa ON inv.product_id = pa.product_id
            WHERE inv.warehouse_id = 7
            AND (inv.pi_sellable > 0 OR inv.pi_onway > 0 OR inv.pi_reserved > 0)
            """
            df = db.read_sql_to_dataframe(sql)
    except Exception as e:
        print(e)
        df = pd.DataFrame()

    return df
