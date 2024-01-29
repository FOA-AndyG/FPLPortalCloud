import os
from datetime import datetime, timedelta

import pandas as pd

from Database.mysql_handler import SQLAlchemyHandler
from Django_Project.settings import EXCEL_FILE_PATH


def get_picking_list(db, warehouse_code):
    print("get_picking_list")
    current_day = datetime.strftime(datetime.now() + timedelta(days=-6), '%Y-%m-%d')
    try:
        base_sql = f"""
            SELECT *
            FROM picking
            WHERE warehouse_id = {warehouse_code}
            AND picking_add_time > '{current_day}'
            ORDER BY picking_code desc
            """
        result_df = db.read_sql_to_dataframe(base_sql)
        return result_df
    except Exception as e:
        print(e)
        return pd.DataFrame()


def get_picking_list_no_db(wh_number):
    print("get_picking_list")
    #             or picking_code = "PL72204040003"
    current_day = datetime.strftime(datetime.now() + timedelta(days=-8), '%Y-%m-%d')
    try:
        base_sql = f"""
            SELECT *
            FROM picking
            WHERE warehouse_id = {wh_number} 
            AND picking_add_time > '{current_day}'
            ORDER BY picking_code desc
            """
        with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                               password="A!05FOA2021edi") as db:
            result_df = db.read_sql_to_dataframe(base_sql)
        return result_df
    except Exception as e:
        print(e)
        return pd.DataFrame()


def get_product_file_path_df(picking):
    print("get_product_file_path_df")
    try:
        base_sql = f"""
        SELECT p.picking_code, p.order_id, p.order_code, o.reference_no, p.product_barcode, p.pd_quantity
        ,b.oab_firstname
        ,b.oab_postcode
        ,b.oab_state
        ,b.oab_city
        ,b.oab_street_address1
        ,p.pick_sort
        ,p.lc_code
        ,sm_code
        ,shipping_fee_estimate
        ,parcel_quantity
        ,a.oat_file_path
        ,a.oat_file_type
        ,a.oat_file_note
        ,pd.box_id
        ,pd.box_num
        FROM picking_detail as p
        LEFT JOIN orders as o ON p.order_id = o.order_id
        LEFT JOIN order_attached AS a ON p.order_id = a.order_id
        LEFT JOIN order_pack_detail as pd ON p.order_code = pd.order_code AND p.product_barcode = pd.product_barcode
        LEFT JOIN order_address_book AS b ON p.order_id = b.order_id
        WHERE p.picking_code = '{picking}'
        GROUP BY p.order_code, p.product_barcode, pd.box_num
        ORDER BY p.pick_sort, p.lc_code, p.product_barcode, p.order_code asc
        """
        with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                               password="A!05FOA2021edi") as db:
            result_df = db.read_sql_to_dataframe(base_sql)

        if not result_df.empty and result_df is not None:
            content = {
                "result": True,
                "result_df": result_df
            }
        else:
            content = {
                "result": False,
                "msg": "Deliver method is not from ALL_SELF_LABEL"
            }
    except Exception as e:
        content = {
            "result": False,
            "msg": str(e)
        }
    return content


def get_picking_details_df(db, picking):
    try:
        base_sql = f"""
        SELECT p.picking_code, p.order_code, p.lc_code, p.product_barcode
        ,p.pd_quantity
        ,o.reference_no
        ,s.tracking_number
        ,oa.multiple_tracking_number
        ,o.sm_code
        ,b.oab_firstname
        ,b.oab_postcode
        ,b.oab_state
        ,b.oab_city
        ,b.oab_street_address1
        ,o.remark
        FROM picking_detail as p
        LEFT JOIN orders as o ON p.order_id = o.order_id
        LEFT JOIN order_additional AS oa ON p.order_id = oa.order_id
        LEFT JOIN order_attached AS a ON p.order_id = a.order_id
        LEFT JOIN order_pack_detail as pd ON p.order_code = pd.order_code AND p.product_barcode = pd.product_barcode
        LEFT JOIN order_address_book AS b ON p.order_id = b.order_id
        LEFT JOIN ship_order AS s ON p.order_id = s.order_id
        WHERE p.picking_code = '{picking}'
        GROUP BY p.order_code, p.product_barcode, pd.box_num
        ORDER BY p.pick_sort, p.lc_code, p.product_barcode, p.order_code asc
        """
        result_df = db.read_sql_to_dataframe(base_sql)

        if not result_df.empty and result_df is not None:
            content = {
                "result": True,
                "result_df": result_df
            }
        else:
            content = {
                "result": False,
                "msg": "Deliver method is not from ALL_SELF_LABEL"
            }
    except Exception as e:
        content = {
            "result": False,
            "msg": "get_picking_details_df: " + str(e)
        }
    return content


def get_container_list():
    print("get_container_list")
    #             or picking_code = "PL72204040003"
    try:
        base_sql = """
            SELECT receiving_code, tracking_number, customer_code, container_type, receiving_add_time
            FROM receiving
            WHERE warehouse_id = 7 AND receiving_status != 0 
            ORDER BY receiving_add_time desc
            LIMIT 1000
            """
        with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                               password="A!05FOA2021edi") as db:
            result_df = db.read_sql_to_dataframe(base_sql)
        # print(result_df)
        return result_df
    except Exception as e:
        print(e)
        return pd.DataFrame()


def export_picking_detail(request):
    try:
        picking = request.POST.get('picking_select')
        print(picking)
        with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                               password="A!05FOA2021edi") as db:
            result_dic = get_picking_details_df(db, picking)
        df = result_dic["result_df"]
        df = df.fillna('')

        # columns_list = ["oat_file_path", "oat_file_type", "oat_file_note"]
        # df = df.drop(columns=columns_list)

        file_path = f"{EXCEL_FILE_PATH}/attachment_files/{picking}/"
        if not os.path.exists(file_path):
            os.makedirs(file_path, 777)

        download_path = f"{file_path}{picking}_details.xlsx"
        df.to_excel(download_path, index=False)
        result_download_path = f"OMSOrderApp/attachment_files/{picking}/{picking}_details.xlsx"
        return result_download_path

    except Exception as e:
        print(e)
        return ""
