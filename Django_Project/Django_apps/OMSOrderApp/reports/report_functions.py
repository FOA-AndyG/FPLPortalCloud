import os
from datetime import datetime

import pandas as pd
from django.http import HttpResponse

from Database.mysql_handler import SQLAlchemyHandler
from Django_Project.settings import EXCEL_FILE_PATH
from Django_apps.HomeApp.functions.session_function import get_session_user_username


def process_order_sales_report(request, df_columns, export_df_columns):
    try:
        branch = request.POST.get("branch_select")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        if branch == "ALL":
            base_sql = f"""
            SELECT o.order_code, o.reference_no, o.customer_code
            , p.product_barcode, p.product_title
            , p.op_quantity, p.product_declared_value
            , s.so_ship_time
            FROM orders o
            LEFT JOIN order_product p ON o.order_id = p.order_id
            LEFT JOIN ship_order s ON o.order_id = s.order_id
            WHERE o.warehouse_id = 7
            AND o.reference_no LIKE 'FOA%%'
            AND (s.so_ship_time > '{start_date} 00:00' and s.so_ship_time < '{end_date} 23:59')
            order by s.so_ship_time desc
            """
        else:
            base_sql = f"""
            SELECT o.order_code, o.reference_no, o.customer_code
            , p.product_barcode, p.product_title
            , p.op_quantity, p.product_declared_value
            , s.so_ship_time
            FROM orders o
            LEFT JOIN order_product p ON o.order_id = p.order_id
            LEFT JOIN ship_order s ON o.order_id = s.order_id
            WHERE o.warehouse_id = 7
            AND o.reference_no LIKE '{branch}%%'
            AND (s.so_ship_time > '{start_date} 00:00' and s.so_ship_time < '{end_date} 23:59')
            order by s.so_ship_time desc
            """

        with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                               password="A!05FOA2021edi") as db:
            result_df = db.read_sql_to_dataframe(base_sql)
        # todo add tracking into the datatable 06/15/22

        # todo: get data from direct sale table
        with SQLAlchemyHandler() as db:
            base_sql = """
                SELECT * 
                FROM itweb.fpl_direct_sale_pricing_log;
            """
            direct_sale_price_df = db.read_sql_to_dataframe(base_sql)

        result_df = result_df.merge(direct_sale_price_df, how="left", left_on="product_barcode", right_on="sku")

        result_df['so_ship_time'] = result_df["so_ship_time"].astype(str)
        for index, row in result_df.iterrows():
            # get branch name
            result_df.loc[index, "branch"] = str(row["reference_no"])[:5]
            # total price
            if row["product_declared_value"] and row["op_quantity"]:
                result_df.loc[index, "total_price"] = float(row["price"]) * float(row["op_quantity"])
            else:
                result_df.loc[index, "total_price"] = 0
            # date format
            if row["so_ship_time"] and row["so_ship_time"] != '':
                result_df.loc[index, "so_ship_time"] = datetime.strptime(row["so_ship_time"].split(" ", 1)[0], "%Y-%m-%d").strftime("%m/%d/%Y")
            # result_df.loc[index, "so_ship_time"] = datetime.strftime(row["so_ship_time"], "%m/%d/%Y")
            # print(datetime.strftime(row["so_ship_time"], "%m/%d/%Y"), result_df.loc[index, "so_ship_time"])
        # print(result_df)

        result_df.loc["Total"] = result_df.sum(numeric_only=True)
        result_df.loc["Total", "product_declared_value"] = ""
        # rename columns
        result_df = result_df[export_df_columns]
        result_df.columns = df_columns
        result_df = result_df.fillna('')
        # print(result_df)

        file_save_path = f"{EXCEL_FILE_PATH}/report_files/order_sales_report/{get_session_user_username(request)}/"
        if not os.path.exists(file_save_path):
            os.makedirs(file_save_path, 777)
        current_time = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
        file_name = f"{branch}_{start_date}_{end_date}.xlsx"
        result_df.to_excel(file_save_path+file_name, index=False)

        excel = open(file_save_path + file_name, "rb")
        response = HttpResponse(excel,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return {"result": True, "response": response, "msg": f"Success: {file_name} has been exported."}
        # download_file_path = f"OMSOrderApp/report_files/order_sales_report/{get_session_user_username(request)}/{result_file_name}"
        # return download_file_path
    except Exception as e:
        print("process_order_sales_report: ", e)
        return {"result": False, "msg": "Error: " + str(e)}


def get_display_data():
    try:
        base_sql = f"""
            SELECT o.order_code, o.reference_no
            , p.product_barcode
            , p.product_title
            , p.product_declared_value
            , p.op_quantity
            , s.so_ship_time
            FROM orders o
            LEFT JOIN order_product p ON o.order_id = p.order_id
            LEFT JOIN ship_order s ON o.order_id = s.order_id
            WHERE o.warehouse_id = 7
            AND o.reference_no LIKE 'FOA%%'
            order by s.so_ship_time desc
            LIMIT 200
            """
        with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                               password="A!05FOA2021edi") as db:
            result_df = db.read_sql_to_dataframe(base_sql)
            # print(result_df)

        # todo: get data from direct sale table
        with SQLAlchemyHandler() as db:
            base_sql = """
                SELECT * 
                FROM itweb.fpl_direct_sale_pricing_log;
            """
            direct_sale_price_df = db.read_sql_to_dataframe(base_sql)

        result_df = result_df.merge(direct_sale_price_df, how="left", left_on="product_barcode", right_on="sku")

        for index, row in result_df.iterrows():
            # get branch name
            result_df.loc[index, "branch"] = str(row["reference_no"])[:5]
            # total price
            if row["product_declared_value"] and row["op_quantity"]:
                result_df.loc[index, "total_price"] = float(row["price"]) * float(row["op_quantity"])
            else:
                result_df.loc[index, "total_price"] = 0
        result_df.loc["Total"] = result_df.sum(numeric_only=True)
        result_df = result_df.fillna('')
        # print(result_df)
        return result_df
    except Exception as e:
        print("get_display_data: ", e)
        return pd.DataFrame()


def get_branch_sql_name():
    branch_map = {
        "ALL": "FOA",
        "FOAEC": "FOAEC"
    }


# add 08/16/2022
def process_order_sales_report_new(request, df_columns, export_df_columns):
    try:
        branch = request.POST.get("branch_select")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        if branch == "ALL":
            base_sql = f"""
            SELECT o.order_code, o.reference_no, o.customer_code
            , p.product_barcode, p.product_title
            , p.op_quantity, p.product_declared_value
            , s.so_ship_time
            FROM orders o
            LEFT JOIN order_product p ON o.order_id = p.order_id
            LEFT JOIN ship_order s ON o.order_id = s.order_id
            WHERE o.warehouse_id = 7
            AND o.reference_no LIKE 'FOA%%'
            AND (s.so_ship_time > '{start_date}' and s.so_ship_time < '{end_date}')
            order by s.so_ship_time desc
            """
        else:
            base_sql = f"""
            SELECT o.order_code, o.reference_no, o.customer_code
            , p.product_barcode, p.product_title
            , p.op_quantity, p.product_declared_value
            , s.so_ship_time
            FROM orders o
            LEFT JOIN order_product p ON o.order_id = p.order_id
            LEFT JOIN ship_order s ON o.order_id = s.order_id
            WHERE o.warehouse_id = 7
            AND o.reference_no LIKE '{branch}%%'
            AND (s.so_ship_time > '{start_date}' and s.so_ship_time < '{end_date}')
            order by s.so_ship_time desc
            """

        with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                               password="A!05FOA2021edi") as db:
            result_df = db.read_sql_to_dataframe(base_sql)
        # get data from direct sale table
        with SQLAlchemyHandler() as db:
            base_sql = """
            
            """
            direct_sale_price_df = db.read_sql_to_dataframe(base_sql)

        result_df['so_ship_time'] = result_df["so_ship_time"].astype(str)
        for index, row in result_df.iterrows():
            # get branch name
            result_df.loc[index, "branch"] = str(row["reference_no"])[:5]
            # total price
            if row["product_declared_value"] and row["op_quantity"]:
                result_df.loc[index, "total_price"] = float(row["product_declared_value"]) * float(row["op_quantity"])
            else:
                result_df.loc[index, "total_price"] = 0
            # date format
            if row["so_ship_time"] and row["so_ship_time"] != '':
                result_df.loc[index, "so_ship_time"] = datetime.strptime(row["so_ship_time"].split(" ", 1)[0], "%Y-%m-%d").strftime("%m/%d/%Y")
            # result_df.loc[index, "so_ship_time"] = datetime.strftime(row["so_ship_time"], "%m/%d/%Y")
            # print(datetime.strftime(row["so_ship_time"], "%m/%d/%Y"), result_df.loc[index, "so_ship_time"])
        # print(result_df)

        result_df.loc["Total"] = result_df.sum(numeric_only=True)
        result_df.loc["Total", "product_declared_value"] = ""
        # rename columns
        result_df = result_df[export_df_columns]
        result_df.columns = df_columns
        result_df = result_df.fillna('')
        # print(result_df)

        file_save_path = f"{EXCEL_FILE_PATH}/report_files/order_sales_report/{get_session_user_username(request)}/"
        if not os.path.exists(file_save_path):
            os.makedirs(file_save_path, 777)
        current_time = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
        file_name = f"{branch}_{start_date}_{end_date}.xlsx"
        result_df.to_excel(file_save_path+file_name, index=False)

        excel = open(file_save_path + file_name, "rb")
        response = HttpResponse(excel,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return {"result": True, "response": response, "msg": f"Success: {file_name} has been exported."}
        # download_file_path = f"OMSOrderApp/report_files/order_sales_report/{get_session_user_username(request)}/{result_file_name}"
        # return download_file_path
    except Exception as e:
        print("process_order_sales_report: ", e)
        return {"result": False, "msg": "Error: " + str(e)}
