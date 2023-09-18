import os
from datetime import datetime

import pandas as pd
from django.http import HttpResponse

from Database.mysql_handler import SQLAlchemyHandler
from Django_apps.HomeApp.functions.session_function import get_session_user_username


def process_tracking_find(request):
    print()
    file_path = f"static/OMSOrderApp/tracking_files/{get_session_user_username(request)}/"
    if not os.path.exists(file_path):
        os.makedirs(file_path, 777)

    try:
        import_file = request.FILES['import_file_path']
        # file_df = pd.read_excel(import_file, sheet_name="SOFS STS Shipping")
        file_df = pd.read_excel(import_file)

        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        base_sql = f"""
        SELECT order_code, sp_code, tracking_number,
        warehouse_id,sm_code,so_status,so_shipping_fee,so_ship_time
        FROM wms.ship_order
        where warehouse_id = 7 and sp_code = 'FPUPS' and so_status = 1
        and (so_ship_time > '{start_date}' and so_ship_time < '{end_date}')
        """

        with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                               password="A!05FOA2021edi") as db:
            sql_df = db.read_sql_to_dataframe(base_sql)

        extra_columns = ["sp_code", "warehouse_id", "sm_code", "so_status", "so_ship_time"]
        result_df = file_df.merge(sql_df, how="left", left_on="Tracking Number", right_on="tracking_number").drop(columns=extra_columns)
        result_df["Difference"] = result_df["so_shipping_fee"] - result_df["Total Charge"]
        result_df = result_df.rename(columns={"so_shipping_fee": "FPLShippingFee"})

        file_name = f"UPS_FPL_Tracking_{start_date}_to_{end_date}.xlsx"
        result_df.to_excel(file_path+file_name, index=False)

        excel = open(file_path+file_name, "rb")
        response = HttpResponse(excel,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return {"result": True, "response": response, "msg": f"Success: {file_name} has been exported."}
    except Exception as e:
        print("process_tracking_find:", e)
        return {"result": False, "msg": "Error: " + str(e)}
