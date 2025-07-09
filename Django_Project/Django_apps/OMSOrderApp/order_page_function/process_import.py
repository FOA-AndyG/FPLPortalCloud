import os
import sys
from datetime import datetime
from io import BytesIO

import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

from Django_Project.settings import EXCEL_FILE_PATH
from Django_apps.HomeApp.functions.session_function import get_session_user_username
from Django_apps.OMSOrderApp.api_handler.oms_api import *
from Django_apps.OMSOrderApp.models import *


# test_mode = True
#
# if test_mode:
#     # enable print
#     sys.stdout = sys.__stdout__
# else:
#     # block print
#     sys.stdout = open(os.devnull, 'w')


# main process function
from Django_apps.OMSOrderApp.picking_functions.scan_support_functions import get_wms_product_dimension


def process_import(request):
    import time
    start_time = time.time()
    content = {
        "result": False,
        "msg": ""
    }
    user_name = get_session_user_username(request)
    # 1. save the file into the local folder, and return a new path for the file
    file_result = save_import_order_file(request)
    if file_result["result"]:
        try:
            file_path = file_result["path"]
            # print(file_path)
            order_df = pd.read_excel(file_path, "批量数据导入").fillna("")
            order_product_df = pd.read_excel(file_path, "产品信息").fillna("")
            order_product_df['SKU'] = order_product_df.SKU.astype(str)
            # print(order_df)
            # print(order_product_df)
            # todo add. check if duplicated 导入编号
            order_no_result = check_duplicate_order_no(order_df)
            if not order_no_result["result"]:
                return order_no_result
            # 2. read the file into dataframe and check if columns are match requirements
            column_result = check_file_column(set(order_df.columns), set(order_product_df.columns))
            # save_data_from_file_path_to_database(file_result["path"])
            if column_result["result"]:
                print(column_result["msg"])
                # 3. start to process data, checking data before sending data to OMS via API
                process_result = check_data_and_send_to_oms(order_df, order_product_df, user_name)
                # 4. return the process result
                return process_result
            else:
                print(column_result["msg"])
                print(column_result["invalid_order_columns"])
                print(column_result["invalid_order_product_columns"])
                content["msg"] = column_result["msg"]
        except Exception as e:
            print("Column error: ", e)
            content["msg"] = str(e)
    else:
        print("file_result: ", file_result["msg"])
        content["msg"] = file_result["msg"]

    print("--- %s seconds ---" % (time.time() - start_time))
    return content


# 1.
def save_import_order_file(request):
    try:
        file_path = f"{EXCEL_FILE_PATH}/order_files/{get_session_user_username(request)}/"
        if not os.path.exists(file_path):
            os.makedirs(file_path, 777)

        import_file = request.FILES['import_file_path']
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


# 2.
def check_file_column(import_order_column_set, import_order_product_column_set):
    # order_df, order_product_df, column_check_list, option_column_check_list
    # Check order columns
    order_column_set = {'导入编号', '仓库代码/Warehouse Code', '参考编号/Reference Code',
                                  '派送方式/Delivery Style', '客户代码', '销售平台/Sales Platform',
                                  '跟踪号/Tracking number', '客户运单跟踪号/Customer Tracking number',
                                  '币种/Currency', '收件人姓名/Consignee Name', '收件人公司/Consignee Company',
                                  '收件人国家/Consignee Country', '州/Province', '城市/City', '街道/Street',
                                  '街道2/Street2', '街道3/Street3', '邮编/Zip Code', '收件人Email/Consignee Email',
                                  '收件人电话/Consignee Phone', '收件人电话2/Consignee Phone2',
                                  '收件人证件号/Consignee License', '备注/Remark', '装箱服务/Pack Box'}
    option_order_column_set = {'销售平台/Sales Platform', '客户运单跟踪号/Customer Tracking number',
                                         '收件人公司/Consignee Company', '街道2/Street2', '街道3/Street3',
                                         '收件人Email/Consignee Email', '收件人电话2/Consignee Phone2',
                                         '收件人证件号/Consignee License', '备注/Remark', '装箱服务/Pack Box'}
    required_order_column_set = set(order_column_set) ^ set(option_order_column_set)
    order_result_dict = check_file_column_function(import_order_column_set, required_order_column_set, option_order_column_set)

    # Check order product columns
    option_order_product_set = {'英文申报名称/Product Name En', '申报价值/Declared Value'}
    required_order_product_set = {'导入编号', 'SKU', '数量/Quantity'}
    order_product_result_dict = check_file_column_function(import_order_product_column_set, required_order_product_set, option_order_product_set)

    if order_result_dict["result"] and order_product_result_dict["result"]:
        content = {
            "result": True,
            "msg": f"Success: File is okay",
        }
        return content
    else:
        content = {
            "result": False,
            "msg": f"Error: Invalid columns in the file",
            "invalid_order_columns": order_result_dict["invalid_set"],
            "invalid_order_product_columns": order_product_result_dict["invalid_set"],
        }

    return content


# 3.
def check_data_and_send_to_oms(order_df, order_product_df, user_name):
    print("check_data_and_send_to_oms")

    success_df = pd.DataFrame(columns=order_df.columns)
    error_df = pd.DataFrame(columns=order_df.columns)
    error_product_df = pd.DataFrame(columns=order_product_df.columns)
    batch_id = get_import_batch_id()
    # todo, start order loop
    for index, row in order_df.iterrows():
        # check how many products inside of the order
        product_df = order_product_df[order_product_df["导入编号"] == row["导入编号"]]
        # product_df['SKU'] = product_df.SKU.astype(str)
        if len(product_df) < 1:
            # check if the order has no products with it, add the order to the error df
            # error_df = error_df.append(row)
            error_df.loc[index] = row
            error_df.loc[index, "ErrorMessage"] = "Error: No product attached with this order"
        else:
            items_str = ""
            counter = 1
            is_product_ok = True
            # todo, start product loop, to make an items str for data set
            product_dict = {}
            for p_index, p_row in product_df.iterrows():
                # check if the product inventory is available
                inventory_result = check_product_inventory(str(row["客户代码"]), str(row["仓库代码/Warehouse Code"]), str(p_row["SKU"]), int(p_row["数量/Quantity"]))
                if inventory_result["result"]:
                    # process to create order
                    # check if the product is the last one, if it is the last one, item str is different
                    if counter < len(product_df):
                        print("not last product", p_row["SKU"])
                        counter += 1
                        item_str = get_single_order_item_str(str(p_row["SKU"]), p_row["数量/Quantity"], False)
                    else:
                        print("last product", str(p_row["SKU"]))
                        item_str = get_single_order_item_str(str(p_row["SKU"]), p_row["数量/Quantity"], True)

                    items_str += item_str
                    product_dict[p_row["SKU"]] = int(p_row["数量/Quantity"])
                else:
                    print("Wrong SKU: ", str(p_row["SKU"]))
                    # if the product inventory is not available, add the order and product to error df
                    is_product_ok = False
                    # error_df = error_df.append(row)
                    error_df.loc[index] = row
                    error_df.loc[index, "ErrorMessage"] = "Error: product sku is invalid"
                    # error_product_df = error_product_df.append(p_row)
                    error_product_df.loc[p_index] = p_row
                    error_product_df.loc[p_index, "ErrorMessage"] = inventory_result["msg"]
            # end product for loop

            if is_product_ok:
                data_set = {"customer_code": str(row["客户代码"]), "warehouse_code": str(row["仓库代码/Warehouse Code"]),
                            "shipping_method": str(row["派送方式/Delivery Style"]),
                            "reference_no": str(row["参考编号/Reference Code"]),
                            "tracking_no": str(row["跟踪号/Tracking number"]),
                            "country_code": str(row['收件人国家/Consignee Country']), "province": str(row['州/Province']),
                            "city": str(row['城市/City']), "address1": str(row['街道/Street']),
                            "address2": str(row["街道2/Street2"]) if str(row["街道2/Street2"]) else "",
                            "zipcode": str(row['邮编/Zip Code']), "name": str(row['收件人姓名/Consignee Name']),
                            "phone": str(row['收件人电话/Consignee Phone']),
                            "remark": str(row['备注/Remark']) if str(row['备注/Remark']) else "",
                            "final_items_str": get_final_items_str(items_str)}

                # todo 4. all data is set, ready to create the order
                create_result = create_order(**data_set)
                if create_result["result"]:
                    # success_df = success_df.append(row)
                    success_df.loc[index] = row
                    success_df.loc[index, "order_code"] = create_result["order_code"]
                    print(create_result["order_code"])
                    # todo 5. write records into the database
                    write_import_batch_function(batch_id, row, create_result["order_code"], user_name)
                    # todo 6. write product records into the database
                    for key, value in product_dict.items():
                        write_product_import_batch_function(batch_id, create_result["order_code"], str(row["客户代码"]),
                                                            key, value, user_name)
                else:
                    # error_df = error_df.append(row)
                    error_df.loc[index] = row
                    error_df.loc[index, "ErrorMessage"] = create_result["msg"]
                    print(create_result["msg"])
        # end order loop

    result = {
        "result": True,
        "success_df": success_df,
        "error_df": error_df,
        "error_product_df": error_product_df,
    }
    return result


# add. check if duplicated 导入编号
def check_duplicate_order_no(order_df):
    result_df = order_df[order_df.duplicated(subset=['导入编号'], keep='first')]
    if result_df.empty:
        content = {
            "result": True
        }
    else:
        # print(result_df["导入编号"].tolist())
        content = {
            "result": False,
            "msg": f"Error: 重复导入编号：{result_df['导入编号'].tolist()}"
        }
    return content


# utility functions =====================================================
def check_file_column_function(imported_set, required_set, option_set):
    # print(imported_set)
    # print(required_set)
    # print(option_set)
    invalid_set = set()
    required_set_copy = required_set.copy()
    option_set_copy = option_set.copy()
    for x in imported_set:
        if x in required_set:
            required_set_copy.remove(x)
        else:   # file column is not in the required list
            if x in option_set:
                option_set_copy.remove(x)
            else:
                invalid_set.add(x)

    if len(required_set_copy) < 1:
        content = {
            "result": True,
        }
    else:
        content = {
            "result": False,
            "invalid_set": invalid_set
        }

    return content


def get_order_import_batch_id():
    data = OmsOrderImportBatch.objects.all().order_by("-batch_id")[0:5]
    if data:
        batch_id = data[0].batchid + 1
    else:
        batch_id = 1
    return batch_id


def save_data_from_file_path_to_database(file_path):
    try:
        content = {
            "result": True,
            "msg": "Success: Save the data."
        }
        order_df = pd.read_excel(file_path, "批量数据导入")
        order_df = order_df.fillna('')
        order_column_checking_list = ['导入编号', '仓库代码/Warehouse Code', '参考编号/Reference Code',
                                      '派送方式/Delivery Style',  '客户代码', '销售平台/Sales Platform',
                                      '跟踪号/Tracking number', '客户运单跟踪号/Customer Tracking number',
                                      '币种/Currency', '收件人姓名/Consignee Name', '收件人公司/Consignee Company',
                                      '收件人国家/Consignee Country', '州/Province', '城市/City', '街道/Street',
                                      '街道2/Street2', '街道3/Street3', '邮编/Zip Code', '收件人Email/Consignee Email',
                                      '收件人电话/Consignee Phone', '收件人电话2/Consignee Phone2',
                                      '收件人证件号/Consignee License', '备注/Remark', '装箱服务/Pack Box']
        option_order_column_checking_list = ['销售平台/Sales Platform', '客户运单跟踪号/Customer Tracking number',
                                             '收件人公司/Consignee Company', '街道2/Street2', '街道3/Street3',
                                             '收件人Email/Consignee Email', '收件人电话2/Consignee Phone2',
                                             '收件人证件号/Consignee License', '备注/Remark', '装箱服务/Pack Box']


        order_product_df = pd.read_excel(file_path, "产品信息")
        order_product_df = order_product_df.fillna('')
        order_product_checking_list = ['导入编号', 'SKU', '数量/Quantity', '英文申报名称/Product Name En', '申报价值/Declared Value']
        option_order_product_checking_list = ['英文申报名称/Product Name En', '申报价值/Declared Value']

    except Exception as e:
        print(e)


def write_import_batch_function(batch_id, row, order_code, user_name):
    try:
        if str(row["客户运单跟踪号/Customer Tracking number"]):
            tracking_number = str(row["客户运单跟踪号/Customer Tracking number"]).replace(" ", "")
        else:
            tracking_number = ""
        new_batch = OmsOrderImportBatch(batch_id=batch_id, order_id=order_code, customer_code=str(row["客户代码"]),
                                        warehouse_code=str(row["仓库代码/Warehouse Code"]),
                                        reference_code=str(row["参考编号/Reference Code"]),
                                        tracking_number=tracking_number,
                                        delivery_method=str(row["派送方式/Delivery Style"]),
                                        remark=str(row['备注/Remark']) if str(row['备注/Remark']) else "",
                                        username=user_name)
        new_batch.save()
        # print("Order saved: ", order_code)
    except Exception as e:
        print(e)


def write_product_import_batch_function(batch_id, order_code, customer_code, sku, qty, user_name):
    try:
        new_batch = OmsOrderProductImportBatch(batch_id=batch_id, order_id=order_code, customer_code=customer_code,
                                               sku=sku, quantity=qty, username=user_name)
        new_batch.save()
    except Exception as e:
        print(e)


def get_import_batch_id():
    new_batch_id = OmsOrderImportBatch.objects.all().order_by("-batch_id")[0:5]
    if new_batch_id:
        batchID = new_batch_id[0].batch_id + 1
        # print("batchID: " + str(batchID))
    else:
        batchID = 1  # give a random number
    return batchID


# 08/08/2022 add
def fdw_order_process_function(request):
    try:
        # get FDW order info
        import_file = request.FILES['import_file_path']
        file_name = str(import_file.name).replace(".xlsx", "")
        # print(file_name)
        fdw_df = pd.read_excel(import_file, "Sheet0")
        fdw_df = fdw_df.fillna("")

        # create an empty order template for Ecang WMS
        ecang_order_template = generate_ecang_empty_order_template()
        ecang_order_df = ecang_order_template.get("order_df")
        ecang_product_df = ecang_order_template.get("product_df")

        order_no = 0
        for index, row in fdw_df.iterrows():
            # order row
            ecang_order_df.loc[order_no, "导入编号"] = order_no+1
            ecang_order_df.loc[order_no, "仓库代码/Warehouse Code"] = "FURNITUREPROWH"
            ecang_order_df.loc[order_no, "参考编号/Reference Code"] = str(row["Sales Record Number"])
            ecang_order_df.loc[order_no, "派送方式/Delivery Style"] = "FDW_NO_LABEL"
            ecang_order_df.loc[order_no, "跟踪号/Tracking number"] = str(row["Tracking no"])
            ecang_order_df.loc[order_no, "收件人姓名/Consignee Name"] = str(row["Buyer Fullname"])
            ecang_order_df.loc[order_no, "收件人国家/Consignee Country"] = "US"
            ecang_order_df.loc[order_no, "州/Province"] = str(row["Buyer State"])
            ecang_order_df.loc[order_no, "城市/City"] = str(row["Buyer City"])
            ecang_order_df.loc[order_no, "街道/Street"] = str(row["Buyer Address 1"])
            if str(row["Buyer Address 2"]):
                ecang_order_df.loc[order_no, "街道2/Street2"] = str(row["Buyer Address 2"])
            ecang_order_df.loc[order_no, "邮编/Zip Code"] = str(row["Buyer Zip"]).replace(" ", "-")
            ecang_order_df.loc[order_no, "收件人电话/Consignee Phone"] = str(row["Buyer Phone Number"])

            # product row
            ecang_product_df.loc[order_no, "导入编号"] = order_no+1
            ecang_product_df.loc[order_no, "SKU"] = str(row["Custom Label"]).replace(" ", "")
            ecang_product_df.loc[order_no, "SKU"] = str(row["Custom Label"]).replace("（", "-")
            ecang_product_df.loc[order_no, "SKU"] = str(row["Custom Label"]).replace("）", "")
            ecang_product_df.loc[order_no, "数量/Quantity"] = int(row["Quantity"])

            order_no = order_no+1

        result_file_name = f"order_auto_new_pack_{file_name}.xls"

        file_save_path = f"{EXCEL_FILE_PATH}/order_files/fdw_order_file/{get_session_user_username(request)}/"
        if not os.path.exists(file_save_path):
            os.makedirs(file_save_path, 777)

        with pd.ExcelWriter(file_save_path + result_file_name) as writer:
            ecang_order_df.to_excel(writer, sheet_name="批量数据导入", index=False)
            ecang_product_df.to_excel(writer, sheet_name="产品信息", index=False)

        print("1")
        excel = open(file_save_path + result_file_name, "rb")
        response = HttpResponse(excel, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
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


def generate_ecang_empty_order_template():
    order_columns = ['导入编号', '自动分配仓库', '仓库代码/Warehouse Code', '参考编号/Reference Code',
                     '派送方式/Delivery Style', '销售平台/Sales Platform', '跟踪号/Tracking number', 'COD订单/COD Orders',
                     'COD Value', '币种/Currency', '年龄/Age', '收件人姓名/Consignee Name', '收件人公司/Consignee Company',
                     '收件人国家/Consignee Country', '州/Province', '城市/City', '街道/Street', '街道2/Street2',
                     '街道3/Street3', '门牌号/Doorplate', '邮编/Zip Code', '收件人Email/Consignee Email',
                     '收件人电话/Consignee Phone', '收件人电话2/Consignee Phone2', '收件人证件号/Consignee License',
                     '备注/Remark', '保险服务/Insurance', '投保金额/Insurance Amount', '签名服务/Signature',
                     '平台店铺/Platform Shop','买家ID/Buyers Id', '装箱服务/Pack Box', '是否强制放货/Mandatory Release Cargo',
                     '订单类型/Order Kind', '订购人/Order Payer Name', '订购人证件号/Order Id Number',
                     '订购人电话/Order Payer Phone', '原产国/Order Country Code Origin', '订单销售金额/Order Sales Amount',
                     '订单销售金额币种/Order Sales Currency', '是否ebay平台/Is Platform Ebay', 'ebay物品编码',
                     'ebay平台交易编号', '税金付款方式/Tax Payment Method', 'VAT税号/Vat Tax Code',
                     '收件人EORI号/Consignee EORI', '配货信息/Distribution Information', '收件人税号类型/Consignee Tax Type',
                     'IOSS编号', '保险类型/Type Of Insurance', '货值/Value', '多跟踪号/Multiple Tracking Number']

    product_columns = ['导入编号', 'SKU', '数量/Quantity', '英文申报名称/Product Name En', '申报价值/Declared Value']

    order_df = pd.DataFrame(columns=order_columns)
    product_df = pd.DataFrame(columns=product_columns)
    product_df["数量/Quantity"] = product_df["数量/Quantity"].astype(int)

    return {"order_df": order_df, "product_df": product_df}


def process_check_fedex_order_zone(request):
    try:
        uploaded_file = request.FILES["import_file_path"]

        if not uploaded_file.name.endswith(('.xlsx', '.xls')):
            return {"status": False, "msg": "Error: please upload a valid Excel file. "}

        df_orders = pd.read_excel(uploaded_file)

        # Filter FedEx orders
        df_orders = df_orders[
            df_orders["Delivery Method"].str.contains("fedex", case=False, na=False) &
            df_orders["Tracking No."].astype(str).str.match(r"^\d{12}$")
            ]

        # Fetch zone mapping from the database using Django ORM
        zones_dict = dict(FedexDirectZone.objects.values_list("zipcode", "zone"))

        # substitute missing zones with a default value and only use the first 5 characters of the postcode
        df_orders["Postcode"] = df_orders["Recipient Postal Code"].astype(str).str.slice(0, 5)

        # Assign zones based on zipcode
        df_orders["zone"] = df_orders["Postcode"].map(zones_dict)

        # Apply specific facility mappings
        df_orders["zone"] = df_orders["zone"].fillna("Diamond Bar Facility to Local")  # Default for missing zip codes

        # selected_columns = ['Order Code', 'Tracking Number', 'Sm Code', 'Postcode', 'zone']
        # print("df_orders", df_orders[selected_columns])

        # Split data by zones into separate DataFrames
        df_industry = df_orders[df_orders["zone"].str.startswith("Industry Facility")]
        df_norcal = df_orders[df_orders["zone"].str.startswith("Tracy")]
        df_local = df_orders[df_orders["zone"].str.startswith("Diamond Bar")]
        df_phoenix = df_orders[df_orders["zone"].str.startswith("Phoenix")]

        # At FedEx Ground sort locations (hubs and automated stations):
        # The following items areconsidered non-conveyables:
        # Any package greater than 60 lbs. = 27 kg
        # Any package over 48 inches in length, 27 inches in width, or 27 inches in height
        # = 121 cm in length, 68 cm in width, or 68 cm in height
        # before saving to Excel, need to check product weight and dimensions for non-conveyables at Industry Facility zone
        # 提取SKU中*之前的部分
        df_industry['SKU'] = df_industry['SKU'].astype(str).str.split('*').str[0]
        # Get product dimension data
        df_product_dim = get_wms_product_dimension()
        if df_product_dim.empty:
            return {"status": False, "msg": "Error: Product dimension data is empty."}

        # 将产品尺寸数据与订单数据合并（基于SKU）
        df_industry_merge = pd.merge(df_industry, df_product_dim, on='SKU', how='left')

        # 定义非可运输条件 - 为了保证产品一定能上传送带，将重量和尺寸都减少一定范围
        # 比如原始重量大于27kg的产品，减少到25kg以下，尺寸大于121cm的产品，减少到118cm以下，长度大于68cm的产品，减少到65cm以下，高度和宽度同理
        non_conveyable_conditions = (
                (df_industry_merge['Net Weight of Product'] > 25) |
                (df_industry_merge['length'] > 118) |
                (df_industry_merge['width'] > 65) |
                (df_industry_merge['height'] > 65)
        )
        # 标记非可运输物品
        df_industry_merge['Non-Conveyable'] = non_conveyable_conditions

        # Convert to Excel with multiple sheets
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")

        # calculate the total volume for each sheet
        sum_non_conveyable = df_industry_merge.loc[df_industry_merge['Non-Conveyable'] == True, 'Volume'].sum()
        sum_conveyable = df_industry_merge.loc[df_industry_merge['Non-Conveyable'] == False, 'Volume'].sum()
        volume_data = [
            ['Industry Facility - Non-Conveyable', sum_non_conveyable / 1000000],
            ['Industry Facility - Conveyable', sum_conveyable / 1000000],
            ['NorCal', df_norcal['Volume'].sum() / 1000000],
            ['Diamond Bar Facility', df_local['Volume'].sum() / 1000000],
            ['Phoenix', df_phoenix['Volume'].sum() / 1000000],
        ]
        df_volume = pd.DataFrame(volume_data, columns=['Zone', 'Volume(m³)'])
        df_volume['Expect Container qty of 53ft'] = (df_volume['Volume(m³)'] / 102.2).round(2)
        df_volume.to_excel(writer, index=False, sheet_name="Volume Summary")

        df_industry_merge.to_excel(writer, index=False, sheet_name="Industry Facility")
        df_norcal.to_excel(writer, index=False, sheet_name="NorCal")
        df_local.to_excel(writer, index=False, sheet_name="Diamond Bar Facility to Local")
        df_phoenix.to_excel(writer, index=False, sheet_name="Phoenix")

        writer.close()
        output.seek(0)

        response = HttpResponse(output.read(),
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = "attachment; filename=processed_orders.xlsx"

        return {"status": True, "response": response, "msg": "Success!"}
    except Exception as e:
        print("Error processing FedEx order zone:", str(e))
        return {"status": False, "msg": str(e)}

