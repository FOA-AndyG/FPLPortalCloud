import os

import pandas as pd
from django.http import HttpResponse

from Django_apps.HomeApp.functions.session_function import get_session_user_username


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


def ils_order_process_function(request):
    try:
        # get FDW order info
        import_file = request.FILES['import_file_path']
        file_name = str(import_file.name).replace(".xlsx", "")
        # print(file_name)
        fdw_df = pd.read_excel(import_file, "Outbound")
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
            ecang_order_df.loc[order_no, "参考编号/Reference Code"] = str(row["OB Code"])
            ecang_order_df.loc[order_no, "派送方式/Delivery Style"] = "FDW_NO_LABEL"
            if str(row["Track#"]):
                ecang_order_df.loc[order_no, "跟踪号/Tracking number"] = str(row["Track#"]).replace(".0", "")
            else:
                ecang_order_df.loc[order_no, "跟踪号/Tracking number"] = "Notracking#"
            ecang_order_df.loc[order_no, "收件人姓名/Consignee Name"] = "XXX"
            ecang_order_df.loc[order_no, "收件人国家/Consignee Country"] = "US"

            # ecang_order_df.loc[order_no, "州/Province"] = str(row["Buyer State"])
            ecang_order_df.loc[order_no, "州/Province"] = "XX"
            # ecang_order_df.loc[order_no, "城市/City"] = str(row["Buyer City"])
            ecang_order_df.loc[order_no, "城市/City"] = "xx"
            ecang_order_df.loc[order_no, "街道/Street"] = str(row["Address"])
            # ecang_order_df.loc[order_no, "邮编/Zip Code"] = str(row["Buyer Zip"]).replace(" ", "-")
            ecang_order_df.loc[order_no, "邮编/Zip Code"] = "xxxxx"
            ecang_order_df.loc[order_no, "收件人电话/Consignee Phone"] = str(row["Telephone"])
            ecang_order_df.loc[order_no, "备注/Remark"] = "MP"+str(row["MP"])

            # product row
            ecang_product_df.loc[order_no, "导入编号"] = order_no+1
            ecang_product_df.loc[order_no, "SKU"] = str(row["SKUS"]).replace(" ", "")
            ecang_product_df.loc[order_no, "数量/Quantity"] = int(row["OQty"])

            order_no = order_no+1

        ecang_order_df["跟踪号/Tracking number"] = ecang_order_df["跟踪号/Tracking number"].astype(str)
        result_file_name = f"order_auto_new_pack_{file_name}.xls"

        file_save_path = f"static/OMSOrderApp/order_files/fdw_order_file/{get_session_user_username(request)}/"
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
