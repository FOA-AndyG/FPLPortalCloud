import os
from datetime import datetime
import pandas as pd
from calendar import monthrange

from django.http import HttpResponse

from Database.mssql_handler import MSSQLAlchemyHandler
from Django_apps.HomeApp.functions.session_function import get_session_user_username
from Django_apps.OMSOrderApp.customer_handler.customer_account import get_customer_object


# test
def calculate_storage_fee(request):
    # customer storage free days
    storage_rates = {
        "MTI": 0.37,
        "CIL": 0.4,
        "XCH": 0.4
    }
    customer = request.POST.get("customer_code_select")
    customer_days = {
        "CIL": 30,
        "XCH": 60,
        "MTI": 60
    }
    # 1. reade inventory batch file
    df = read_inventory_batch(request)

    try:
        # 2. get the data if the date over the limit day based on the customer
        free_day = customer_days.get(customer)
        inventory_batch_df = df[df["库龄"] < (free_day + 30)]
        print(len(inventory_batch_df))

        # 3. get product dimension data
        with MSSQLAlchemyHandler() as db:
            sql = f"""
            SELECT product_barcode
                  ,customer_code
                  ,product_status
                  ,product_length
                  ,product_width
                  ,product_height
                  ,product_net_weight
                  ,product_weight
              FROM [ECANGWMS].[dbo].product
              WHERE customer_code = '{customer}' and product_status = 1
            """
            product_df = db.read_sql_to_dataframe(sql)

        # 4. merge inventory batch and product dimension into one dataframe
        result_df = inventory_batch_df.merge(product_df, how="left", left_on="产品代码", right_on="product_barcode")

        # 5. calculate the storage
        total_actual_fee = 0
        from calendar import monthrange
        today_month_days = monthrange(datetime.now().year, datetime.now().month)[1]
        for i, r in result_df.iterrows():
            single_product_volume = (r["product_length"] * r["product_width"] * r["product_height"]) / 1000000
            batch_volume = single_product_volume * r["数量"]

            # result_df.loc[i, "Batch_Volume"] = math.ceil(batch_volume)
            # actual_fee = storage_rates.get(customer) * math.ceil(batch_volume) * int(r["库龄"])

            result_df.loc[i, "Batch_Volume"] = round(batch_volume, 2)
            # actual_fee = storage_rates.get(customer) * round(batch_volume, 2) * int(r["库龄"])

            if customer == "CIL":
                if int(r["库龄"]) <= 30:
                    actual_fee = storage_rates.get(customer) * round(batch_volume, 2) * int(r["库龄"])
                    result_df.loc[i, "Calculate_Day"] = int(r["库龄"])
                else:   # 30 < int(r["库龄"]) < 60:
                    diff_day = 60 - int(r["库龄"])
                    actual_fee = storage_rates.get(customer) * round(batch_volume, 2) * diff_day
                    result_df.loc[i, "Calculate_Day"] = diff_day
            else:
                if int(r["库龄"]) <= 30:
                    actual_fee = storage_rates.get(customer) * round(batch_volume, 2) * int(r["库龄"])
                    result_df.loc[i, "Calculate_Day"] = int(r["库龄"])
                elif 30 < int(r["库龄"]) <= 60:
                    actual_fee = storage_rates.get(customer) * round(batch_volume, 2) * 30
                    result_df.loc[i, "Calculate_Day"] = 30
                else:   # 60 < int(r["库龄"]) <= 90
                    diff_day = 90 - int(r["库龄"])
                    actual_fee = storage_rates.get(customer) * round(batch_volume, 2) * diff_day
                    result_df.loc[i, "Calculate_Day"] = diff_day

            result_df.loc[i, "Batch_Storage_Fee"] = actual_fee
            total_actual_fee += actual_fee

        print("Total Fee: ", total_actual_fee)
        current_time = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
        result_file_name = f"{customer}{current_time}.xlsx"
        result_df.to_excel(result_file_name, index=False)

    except Exception as e:
        print(e)


def read_inventory_batch(request):
    df = pd.DataFrame()
    try:
        import_file = request.FILES['import_file_path']
        df = pd.read_excel(import_file)
    except Exception as e:
        print(e)
    return df


# production
def new_calculate_fee(request):
    # user input
    customer = request.POST.get("customer_code_select")
    import_file = request.FILES['import_file_path']

    # todo: add special deal for CIL => 60 days free rent for each container comes in June, July, and August
    special_free_day = 0
    special_free_day_customer_list = ["CIL"]
    special_free_day_month = ["2022-06", "2022-07", "2022-08"]
    if customer in special_free_day_customer_list:
        special_free_day = 60

    free_day = get_customer_object(customer).freeRentDays
    base_rate = get_customer_object(customer).storageRate

    # todo: add increased storage rate for customer
    increased_storage_customer_list = ["ARJOIN"]
    increased_days_list1 = [30, 90]

    # 1. reade inventory batch file
    df = pd.read_excel(import_file)

    # 2. start to process data
    try:
        total_fee = 0
        for i, r in df.iterrows():
            # check if the customer code is not match
            if r["客户代码(Customer Code)"] not in customer:
                content = {
                    "result": False,
                    "msg": "Error: Customer code in the file is not match, please double-check the file."
                }
                return content
            # start process
            if r["库龄天数(Days)"] <= free_day:
                df.loc[i, "Batch_Storage_Fee"] = 0
                df.loc[i, "Storage_Rule"] = f"0-{str(free_day)}day"
            else:
                # 3. get batch volume
                batch_volume = (r["长/cm(Length)"] * r["宽/cm(Width)"] * r["高/cm(Height)"] / 1000000) * r["数量(Quantity)"]

                # 07/21/2022 check if customer container receives date < special free day
                # if customer in special_free_day_customer_list:
                #     if any(element in r["入库日期(Inbound Date)"] for element in special_free_day_month):
                #         if r["库龄天数(Days)"] <= special_free_day:
                #             batch_fee = 0
                #             df.loc[i, "Storage_Rule"] = f"{str(free_day)}-{str(special_free_day)}day"

                # 09/05/2023 for increased rate
                if customer in increased_storage_customer_list:
                    if r["库龄天数(Days)"] > increased_days_list1[1]:
                        batch_fee = batch_volume * 0.398
                        df.loc[i, "Storage_Rule"] = f"{str(increased_days_list1[1])}-9999day"
                    elif r["库龄天数(Days)"] > increased_days_list1[0]:
                        batch_fee = batch_volume * 0.348
                        df.loc[i, "Storage_Rule"] = f"{str(increased_days_list1[0])}-{str(increased_days_list1[1])}day"
                    else:
                        batch_fee = batch_volume * 0
                        df.loc[i, "Storage_Rule"] = f"0-{str(increased_days_list1[0])}day"
                else:
                    batch_fee = batch_volume * base_rate
                    df.loc[i, "Storage_Rule"] = f"{str(free_day)}-9999day"

                df.loc[i, "batch_volume"] = batch_volume
                df.loc[i, "Batch_Storage_Fee"] = batch_fee
                total_fee += batch_fee

        df.loc[0, "Total_Storage_Fee"] = round(total_fee, 2)
        current_time = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
        result_file_name = f"{customer}{current_time}.xlsx"

        file_save_path = f"static/OMSOrderApp/report_files/storage_fee_report/{get_session_user_username(request)}/"
        if not os.path.exists(file_save_path):
            os.makedirs(file_save_path, 777)

        df.to_excel(file_save_path+result_file_name, index=False)

        excel = open(file_save_path+result_file_name, "rb")
        response = HttpResponse(excel,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={result_file_name}'
        content = {
            "result": True,
            "response": response,
            "msg": "Success!"
        }
    except Exception as e:
        content = {
            "result": False,
            "msg": f"Error: {str(e)}"
        }
    return content


# Todo add: 08/08/2022
def only_calculate_FBA_list():
    print()
