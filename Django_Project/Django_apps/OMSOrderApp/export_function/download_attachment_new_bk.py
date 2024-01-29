import os
import time

import numpy as np
from PyPDF2 import PdfFileMerger
from datetime import datetime, timedelta
import asyncio
import pandas as pd
import pysftp
import requests
import shutil

from Database.mssql_handler import MSSQLAlchemyHandler
from Database.mysql_handler import SQLAlchemyHandler

# label check function
# C:\Program Files\Tesseract-OCR
from pdf2image import convert_from_path
import pytesseract

from Django_Project.settings import EXCEL_FILE_PATH
from Django_apps.OMSOrderApp.models import OmsLabelInfo


def LabelOCR(file):
    # print(file)
    text_arr = []
    pdf = convert_from_path(file, 300, poppler_path=r"C:\Program Files\poppler-22.01.0\Library\bin")
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    for page_number, page_data in enumerate(pdf):
        # print('Page :' + str(page_number))
        text = pytesseract.image_to_string(page_data).replace(" ", "").upper()  # .encode("utf-8")
        print(text)
        text_arr.append(text)
    return text_arr


def CheckLabel(product_sku, oab_firstname, file):
    text_arr = LabelOCR(file)
    OK = True
    if not (any(product_sku.upper() in string for string in text_arr)):
        OK = False
    if not (any(oab_firstname.upper() in string for string in text_arr)):
        OK = False
    return OK


async def process_df(**kwargs):
    # batch_no, df, sftp, self_label_path, temp_pdf_file_path, fp_ups_path, temp_img_file_path
    counter = 0
    miss_list = []
    merger = PdfFileMerger()
    for index, row in kwargs.get("df").iterrows():
        # if "ALL_SELF_LABEL" in row["sm_code"]:
        print(kwargs.get("batch_no"), index)
        if "SELF" in row["sm_code"]:
            if row["oat_file_path"] != '':
                # print(row["oat_file_path"])
                # print("1")
                try:
                    # copy file from the wms server pathe
                    kwargs.get("sftp").get(kwargs.get("self_label_path") + row["oat_file_path"],
                                           localpath=kwargs.get("temp_pdf_file_path") + str(row["oat_file_note"]))
                    # print("2")
                    merger.append(kwargs.get("temp_pdf_file_path") + str(row["oat_file_note"]),
                                  import_bookmarks=False)
                    counter += 1

                    # todo: insert a data record with file path into the database
                    # ab_path = '\EL-ANDYG\Users\Andy Guo\Desktop\AndyG\FPLPortal\Django_Project\static\OMSOrderApp\attachment_files'
                    # data_obj = OmsLabelInfo(order_id=row["order_code"], sku="product_barcode",
                    #                         label_path=temp_pdf_file_path+str(row["oat_file_note"]),
                    #                         is_scan=0, wms_tracking="reference_no",
                    #                         is_label_correct=0)
                    # data_obj.save()

                    # todo: call Chris's function to double check label info
                    # product_sku = str(row["product_barcode"]).split("-", 1)[1].replace(" ", "").upper()
                    # oab_firstname = row["oab_firstname"].replace(" ", "").upper()
                    # label_path = temp_pdf_file_path + str(row["oat_file_note"])
                    # if CheckLabel(product_sku, oab_firstname, label_path):
                    #     merger.append(temp_pdf_file_path + str(row["oat_file_note"]), import_bookmarks=False)
                    #     counter += 1
                    # else:
                    #     wrong_label_list.append(row["order_code"])
                    #     print("Wrong labels: ", row["order_code"], product_sku, oab_firstname)

                except Exception as e:
                    print(row["order_code"], " = ", row["oat_file_path"], ": ", e)
                    miss_list.append(row["order_code"])
            else:
                print(row["product_barcode"])
                if "EC" in row["reference_no"]:
                    # todo: create a label pdf
                    ec_sku = ec_oms_xref(row["product_barcode"])
                    print("EC sku:", ec_sku)
                    ec_label = foa_generate_label(title="FOA EC", ref_no=row["reference_no"],
                                                  order_no=row["order_code"], sku=row["product_barcode"],
                                                  ec_sku=ec_sku, file_path=kwargs.get("temp_pdf_file_path"))
                    print(ec_label)
                    merger.append(ec_label, import_bookmarks=False)
                    counter += 1
                    # miss_list.append(row["order_code"])
                else:
                    miss_list.append(row["order_code"])

        # elif "FP_UPS" in row["sm_code"]:
        elif "UPS" in row["sm_code"]:
            try:
                # copy file from the wms server path
                file_num = str(int(row["box_num"]) - 1)
                img_file_name = f"/{file_num}.gif"
                local_img_file_name = f"{row['order_code']}-{file_num}.gif"
                local_pdf_file_name = f"{row['order_code']}-{file_num}.pdf"
                kwargs.get("sftp").get(kwargs.get("fp_ups_path") + row["order_code"] + img_file_name,
                                       localpath=kwargs.get("temp_img_file_path") + local_img_file_name)
                # print("2")
                # convert gif to pdf
                from PIL import Image
                image_1 = Image.open(kwargs.get("temp_img_file_path") + local_img_file_name)
                im_1 = image_1.convert('RGB')
                im_1.save(kwargs.get("temp_img_file_path") + local_pdf_file_name)
                # merge pdf into one
                merger.append(kwargs.get("temp_img_file_path") + local_pdf_file_name,
                              import_bookmarks=False)
                # print("3")
                counter += 1
            except Exception as e:
                print(e)
                miss_list.append(row["order_code"])

        await asyncio.sleep(0.2)
    content = {
        "merger": merger,
        "miss_list": miss_list,
        "counter": counter
    }
    return content


async def process_download_attachment(request):
    try:
        picking = request.POST.get('picking_select')

        file_path = f"{EXCEL_FILE_PATH}/attachment_files/{picking}/"
        if not os.path.exists(file_path):
            os.makedirs(file_path, 777)

        temp_pdf_file_path = f"{EXCEL_FILE_PATH}/attachment_files/{picking}/temp/pdf/"
        if not os.path.exists(temp_pdf_file_path):
            os.makedirs(temp_pdf_file_path, 777)

        temp_img_file_path = f"{EXCEL_FILE_PATH}/attachment_files/{picking}/temp/img/"
        if not os.path.exists(temp_img_file_path):
            os.makedirs(temp_img_file_path, 777)

        result_dic = get_product_file_path_df(picking)
        if result_dic["result"]:
            df = result_dic["result_df"]
            df = df.fillna('')
            # print(df)
            # separate data into ups_df and fedex_df
            # ups_df = pd.DataFrame(columns=df.columns)
            # fedex_df = pd.DataFrame(columns=df.columns)
            # for i, r in df.iterrows():
            #     # ups reference no over 12
            #     if len(r["reference_no"]) > 12:
            #         ups_df.loc[i] = r
            #     else:
            #         fedex_df.loc[i] = r

            # print(ups_df)
            # print(fedex_df)
            merger = PdfFileMerger()
            counter = 0

            # updated version: check if using FP_UPS
            miss_list = []
            wrong_label_list = []
            fp_ups_path = "/data/www/trunk/wms/data/gif/"
            self_label_path = "/data/www/trunk/oms"
            sftp = get_connection_for_eccang_sftp()

            if sftp:
                # todo: run 2 tasks at the same time
                # batch_no, df, sftp, self_label_path, temp_pdf_file_path, fp_ups_path, temp_img_file_path
                df_chunks = np.array_split(df, 2)
                content1, content2 = await asyncio.gather(process_df(batch_no=1, df=df_chunks[0], sftp=sftp,
                                                                     self_label_path=self_label_path,
                                                                     temp_pdf_file_path=temp_pdf_file_path,
                                                                     fp_ups_path=fp_ups_path,
                                                                     temp_img_file_path=temp_img_file_path),
                                                          process_df(batch_no=2, df=df_chunks[1], sftp=sftp,
                                                                     self_label_path=self_label_path,
                                                                     temp_pdf_file_path=temp_pdf_file_path,
                                                                     fp_ups_path=fp_ups_path,
                                                                     temp_img_file_path=temp_img_file_path))

                sftp.close()
                counter = content1["content1"] + content2["content2"]
                miss_list.append(content1["miss_list"])
                miss_list.append(content2["miss_list"])
                merger1 = content1["merger"]
                merger2 = content2["merger"]
            print(counter)
            if counter > 0:
                current_time = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
                merger.write(file_path + picking + "-" + current_time + ".pdf")
                download_path = f"OMSOrderApp/attachment_files/{picking}/"
                content = {
                    "result": True,
                    "result_path": download_path + picking + "-" + current_time + ".pdf",
                    "msg": f" [{counter}] files have been merged into one file, please click Download button to download",
                    "miss_list": miss_list,
                    "wrong_label_list": wrong_label_list
                }
            else:
                content = {
                    "result": False,
                    "msg": "No attachment files found.",
                    "miss_list": miss_list,
                    "wrong_label_list": wrong_label_list
                }
            merger.close()
            return content
        else:
            # print(result_dic["msg"])
            return result_dic
    except Exception as e:
        # print(e)
        content = {
            "result": False,
            "msg": str(e)
        }
        return content


def get_connection_for_eccang_sftp():
    try:
        HOSTNAME = "34.96.174.105"
        USERNAME = "eccang"
        PASSWORD = "eccang123"
        KEY_PATH = "{EXCEL_FILE_PATH}/eccang_server_key/eccang"

        # cnopts = pysftp.CnOpts(knownhosts=KEY_PATH)
        # sftp = pysftp.Connection(HOSTNAME, username=USERNAME, private_key_pass=PASSWORD, cnopts=cnopts)
        sftp = pysftp.Connection(HOSTNAME, username=USERNAME, private_key=KEY_PATH, private_key_pass=PASSWORD)

        return sftp
    except Exception as e:
        print(e)
        return None


def get_picking_list():
    print("get_picking_list")
    #             or picking_code = "PL72204040003"
    try:
        base_sql = """
            SELECT *
            FROM picking
            WHERE warehouse_id = 7 AND (pick_status = 0 OR pick_status = 1) 
            AND (pda_picking_status = 0 OR pda_picking_status = 1)
            or picking_code = "PL72204260001"
            ORDER BY picking_code desc
            """
        with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                               password="A!05FOA2021edi") as db:
            result_df = db.read_sql_to_dataframe(base_sql)
        # print(result_df)
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


def foa_generate_label(title, order_no, sku, ref_no, ec_sku, file_path):
    zpl_label = f"""
    ^XA
    ^FX Top section with logo, name and address.
    ^CF0,80
    ^FO200,150^FD{title}^FS
    
    ^FO50,250^GB700,3,3^FS
    
    ^FX Second section with recipient address and permit information.
    ^CF0,35
    ^FO130,300^FDOrder No: {order_no}^FS
    ^FO130,380^FDSKU: {sku}^FS
    ^FO130,460^FDEC SKU: {ec_sku}^FS
    ^FO130,540^FDEC Ref1: {ref_no}^FS
    
    ^XZ
    """
    # adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
    url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
    files = {'file': zpl_label}
    headers = {'Accept': 'application/pdf'}  # omit this line to get PNG images back
    response = requests.post(url, headers=headers, files=files, stream=True)

    if response.status_code == 200:
        response.raw.decode_content = True
        file_name = order_no + "_" + sku + ".pdf"
        result_file_path = file_path + file_name
        # print(result_file_path)
        with open(result_file_path, 'wb') as out_file:  # change file name for PNG images
            shutil.copyfileobj(response.raw, out_file)
            # print("Generate EC label")

    else:
        print('Error: ' + response.text)
        result_file_path = ""

    return result_file_path


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


def process_container_label(receive_no, total_number, selected_tracking):
    file_path = f"{EXCEL_FILE_PATH}/container_files/{receive_no}/"
    if not os.path.exists(file_path):
        os.makedirs(file_path, 777)

    merger = PdfFileMerger()
    counter = 0

    current_day = datetime.today().weekday()
    if current_day < 4:
        current_time = datetime.strftime(datetime.now() + timedelta(days=1), "%m/%d/%Y")
    elif current_day == 4:
        current_time = datetime.strftime(datetime.now() + timedelta(days=3), "%m/%d/%Y")
    elif current_day == 5:
        current_time = datetime.strftime(datetime.now() + timedelta(days=2), "%m/%d/%Y")
    else:
        current_time = datetime.strftime(datetime.now() + timedelta(days=1), "%m/%d/%Y")

    for i in range(1, int(total_number) + 1):
        print(i)
        try:
            label_path = generate_container_label(receive_no, selected_tracking, i, file_path, current_time)
            merger.append(label_path, import_bookmarks=False)
            counter += 1
        except Exception as e:
            print(e)
    print("total: ", counter)
    current_time = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
    merger.write(file_path + current_time + ".pdf")
    download_path = f"OMSOrderApp/container_files/{receive_no}/"
    result_download_path = download_path + current_time + ".pdf"
    return result_download_path


def generate_container_label(receive_no, selected_tracking, current_number, file_path, current_time):
    zpl_label = f"""
    ^XA
    ^FX Top section with logo, name and address.
    ^CF0,80
    ^FO50,150^FDNo. {str(current_number)}^FS

    ^FO50,250^GB700,3,3^FS

    ^FX Second section with recipient address and permit information.
    ^CF0,50
    ^FO50,300^FDReceive No: {receive_no}^FS
    ^FO50,400^FDTrailer No: {selected_tracking}^FS
    ^FO50,500^FDTime: {current_time}^FS
    
    ^XZ
    """

    # adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
    url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
    files = {'file': zpl_label}
    headers = {'Accept': 'application/pdf'}  # omit this line to get PNG images back
    response = requests.post(url, headers=headers, files=files, stream=True)

    if response.status_code == 200:
        response.raw.decode_content = True
        file_name = selected_tracking + "_" + str(current_number) + ".pdf"
        result_file_path = file_path + file_name
        # print(result_file_path)
        with open(result_file_path, 'wb') as out_file:  # change file name for PNG images
            shutil.copyfileobj(response.raw, out_file)
            # print("Generate EC label")

    else:
        print('Error: ' + response.text)
        result_file_path = ""

    time.sleep(0.5)
    return result_file_path


# todo: get ex sku xref
def ec_oms_xref(sku):
    base_sql = f"""
    SELECT SageSKU, FactorySKU
    FROM [SageFPL].[dbo].[FPL_Product_Xref]
    WHERE FactorySKU = '{sku}'
    """
    with MSSQLAlchemyHandler() as db:
        result = db.read_sql_to_dataframe(base_sql)
        if result["SageSKU"].iloc[0]:
            ec_sku = result["SageSKU"].iloc[0]
        else:
            ec_sku = "NotFound"
    return ec_sku
    # result = db_conn.read_sql_to_dataframe(base_sql)
    # if result["SageSKU"].iloc[0]:
    #     ec_sku = result["SageSKU"].iloc[0]
    # else:
    #     ec_sku = "NotFound"
    # return ec_sku


def export_picking_detail(request):
    try:
        picking = request.POST.get('picking_select')
        print(picking)
        result_dic = get_product_file_path_df(picking)
        df = result_dic["result_df"]
        df = df.fillna('')

        columns_list = ["oat_file_path", "oat_file_type", "oat_file_note"]
        df = df.drop(columns=columns_list)

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
