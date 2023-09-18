import pandas as pd
import os
from datetime import datetime

from Django_apps.HomeApp.functions.session_function import get_session_user_username
from django.core.files.storage import FileSystemStorage
from Django_apps.ScanApp.models import Containerlog


def scan_info_import_process(request):
    print("scan_info_import_process")
    file_result = save_import_scan_info(request)
    content = {
        "result": False,
        "msg": ""
    }
    if file_result["result"]:
        try:
            file_path = file_result["path"]
            scan_info_df = pd.read_excel(file_path, sheet_name=0)
            current_date = datetime.now()
            user_name = get_session_user_username(request)
            for index, row in scan_info_df.iterrows():
                tracking = str(row['Tracking ID']).split("&")
                if 'AMZL_US_PREMIUM' in row['Ship Method']:
                    for t in tracking:
                        container_log = Containerlog(containerno='AMXL_PREMIUM',
                                                     carrier='AMXL',
                                                     tracking=t,
                                                     createdate=current_date,
                                                     machinename=user_name)
                        container_log.save(using='mssql167')
                elif "AMXL (AMZL_SH)" in row['Ship Method']:
                    for t in tracking:
                        container_log = Containerlog(containerno='AMXL',
                                                     carrier='AMXL',
                                                     tracking=t,
                                                     createdate=current_date,
                                                     machinename=user_name)
                        container_log.save(using='mssql167')
                elif "AMZL" in row['Ship Method']:
                    for t in tracking:
                        container_log = Containerlog(containerno='AMXL',
                                                     carrier='AMXL',
                                                     tracking=t,
                                                     createdate=current_date,
                                                     machinename=user_name)
                        container_log.save(using='mssql167')
                elif "Amazon Shipping" in row['Ship Method']:
                    for t in tracking:
                        container_log = Containerlog(containerno='USPS',
                                                     carrier='USPS',
                                                     tracking=t,
                                                     createdate=current_date,
                                                     machinename=user_name)
                        container_log.save(using='mssql167')
                elif "FedEx (Landmark) Standard" in row['Ship Method']:
                    for t in tracking:
                        container_log = Containerlog(carrier='FedEx',
                                                     tracking=t,
                                                     createdate=current_date,
                                                     machinename=user_name)
                        container_log.save(using='mssql167')
                elif "UPS" in row['Ship Method']:
                    container_no = str(row['Container No'])
                    for t in tracking:
                        container_log = Containerlog(carrier='UPS',
                                                     containerno='UPS' + container_no,
                                                     tracking=t,
                                                     createdate=current_date,
                                                     machinename=user_name)
                        container_log.save(using='mssql167')
            content["result"] = True
            content["msg"] = "Success!"
        except Exception as e:
            content["msg"] = str(e)
    else:
        print("file_result: ", file_result["msg"])
        content["msg"] = file_result["msg"]

    return content


def save_import_scan_info(request):
    try:
        file_path = f"static/ScanApp/scan_info/{get_session_user_username(request)}/"
        if not os.path.exists(file_path):
            os.makedirs(file_path, 777)

        import_file = request.FILES['vc_excel']
        name_time_format = datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S')
        import_file_name = str(import_file.name)

        is_file_okay = True

        if import_file_name.endswith("xlsx"):
            temp_file_name = str(import_file_name).replace('.xlsx', '')
            file_name = f"{temp_file_name}_{name_time_format}.xlsx"
        elif import_file_name.endswith("xls"):
            temp_file_name = str(import_file_name).replace('.xls', '')
            file_name = f"{temp_file_name}_{name_time_format}.xls"
        elif import_file_name.endswith("csv"):
            temp_file_name = str(import_file_name).replace('.csv', '')
            file_name = f"{temp_file_name}_{name_time_format}.csv"
        else:
            file_name = ""
            is_file_okay = False

        if is_file_okay:
            file_system = FileSystemStorage(location=file_path)
            file_system.save(file_name, import_file)
            new_file_full_path = file_path + file_name
            content = {
                "path": new_file_full_path,
                "result": True,
                "msg": "Success: File is saved!",
            }
        else:
            content = {
                "result": False,
                "msg": "Error: Can't read the file",
            }
    except Exception as e:
        print(e)
        content = {
            "result": False,
            "msg": f"Error: {str(e)}",
        }

    return content
