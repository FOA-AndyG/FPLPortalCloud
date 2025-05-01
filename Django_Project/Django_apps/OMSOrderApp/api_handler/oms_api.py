from copy import deepcopy

from zeep import Client, Settings
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

from Django_apps.OMSOrderApp.customer_handler.customer_account import *


def oms_api_call_test(**kwargs):
    settings = Settings(strict=False, xml_huge_tree=True)
    wsdl = 'http://oms.furnitureproslogistics.com/default/svc/wsdl'
    client = Client(wsdl, settings=settings)

    data_dict = {
        "appToken": "f88b7a4b18ebe887ee7b3f5af1e1b8d5",
        "appKey": "39c64b08d11e7f2dcabdead6aa461a2f",
        "service": "getProductList",
        "paramsJson": """{
            "pageSize":10,
            "page":1,
            "product_sku":"",
            "product_sku_arr":[],
            "start_time":"",
            "end_time":"",
            "update_start_time":"",
            "update_end_time":""
        }"""
    }
    with client.settings(raw_response=True):
        # response = client.service.callService(appToken="f88b7a4b18ebe887ee7b3f5af1e1b8d5",
        #  appKey="39c64b08d11e7f2dcabdead6aa461a2f", service="getProductList", paramsJson=params_dict)
        response = client.service.callService(**data_dict)
        # print(response.text)

        soup = BeautifulSoup(response.text, 'xml')

        ns1 = soup.find("ns1:callServiceResponse")

        resp = ns1.find("response")

        parsed = json.loads(resp.text)
        # print(parsed)
        # print(parsed["data"][0])

        first_product = parsed["data"][0]
        print(first_product["product_sku"])

        # print json with nice format
        result_json = json.dumps(parsed, indent=4)
        # print(result_json)

        # print(result_json[7])


def oms_api_call(**kwargs):
    try:
        settings = Settings(strict=False, xml_huge_tree=True)
        wsdl = 'http://oms.furnitureproslogistics.com/default/svc/wsdl'
        client = Client(wsdl, settings=settings)

        content = {
            "result": False,
            "msg": "Empty"
        }
        # customer_no = request.session["customerNo"]

        if kwargs.get("data_dict"):
            data_dict = kwargs.get("data_dict")
            data_dict["appToken"] = get_customer_object(kwargs.get("customer_code")).appToken
            data_dict["appKey"] = get_customer_object(kwargs.get("customer_code")).appKey

            with client.settings(raw_response=True):
                response = client.service.callService(**data_dict)
                soup = BeautifulSoup(response.text, 'xml')
                ns1 = soup.find("ns1:callServiceResponse")
                resp = ns1.find("response")

                parsed = json.loads(resp.text)
                # print(parsed)

                content = {
                    "result": True,
                    "json_response": parsed
                }
                # first_data = parsed["data"][0]
                # print(first_data)

                # result_json = json.dumps(parsed, indent=4)
                # print(result_json)

        return content
    except Exception as e:
        print("API ERROR: ", e)
        content = {
            "result": False,
            "msg": str(e)
        }
        return content


# check the product sellable qty
def check_product_inventory(customer_code, wh_code, sku, order_qty: int):
    data_dict = {
        "service": "getProductInventory",
        "paramsJson": """{
                    "pageSize":1,
                    "page":1,
                    "product_sku":"%s",
                    "product_sku_arr":[],
                    "warehouse_code":"%s", 
                    "warehouse_code_arr":[],
                    "update_start_time":""
                }""" % (sku, wh_code)
    }
    api_result = oms_api_call(customer_code=customer_code, data_dict=data_dict)
    if api_result["result"]:
        response = api_result["json_response"]
        # print(response)
        result_msg = response["ask"]
        # print(result_msg)
        if result_msg == "Success":
            first_data = response["data"][0]
            print("check inv: ", first_data["product_sku"], first_data["sellable"])
            # print("after order qty: ", int(first_data["sellable"]) - order_qty)
            if int(first_data["sellable"]) - order_qty >= 0:
                content = {
                    "result": True,
                }
            else:
                content = {
                    "result": False,
                    "msg": f"Error: Not enough sellable qty for sku {first_data['product_sku']}"
                }
        else:
            content = {
                "result": False,
                "msg": f"Error: {response['message']}"
            }
            # print(content.get("msg"))
        return content
    else:
        return api_result


# create order api function
def create_order(**kwargs):
    # FOANW is for Alex local sales order
    if "FOAEC" in kwargs.get("reference_no") or "FOAJL" in kwargs.get("reference_no"):
        verify = "1"
    else:
        verify = "0"

    data_dict = {
        "service": "createOrder",
        "paramsJson": """{
                    "warehouse_code": "%s",
                    "shipping_method": "%s",
                    "reference_no": "%s",
                    "tracking_no":"%s",
                    "country_code": "%s",
                    "province": "%s",
                    "city": "%s",
                    "address1": "%s",
                    "address2": "%s",
                    "zipcode": "%s",
                    "name": "%s",
                    "phone": "%s",
                    "remark":"%s",
                    %s
                    "is_pack_box": 0,
                    "verify": %s,
                    "label":{
                        "file_type":"pdf",
                        "file_data":"",
                        "file_size":"4x6"
                    }
                }""" % (kwargs.get("warehouse_code"), kwargs.get("shipping_method"),
                        kwargs.get("reference_no"), kwargs.get("tracking_no", ""),
                        kwargs.get("country_code"), kwargs.get("province"), kwargs.get("city"),
                        kwargs.get("address1"),
                        kwargs.get("address2", ""), kwargs.get("zipcode"), kwargs.get("name"),
                        kwargs.get("phone"), kwargs.get("remark", ""), kwargs.get("final_items_str"), verify)
    }
    # print(data_dict)
    api_result = oms_api_call(customer_code=kwargs.get("customer_code"), data_dict=data_dict)
    if api_result["result"]:
        response = api_result["json_response"]
        result_msg = response["ask"]
        if result_msg == "Success":
            content = {
                "result": True,
                "order_code": response["order_code"],
            }
        else:
            content = {
                "result": False,
                "msg": f"Error: {response['message']}"
            }
        return content
    else:
        return api_result


# get order_item_str
def get_single_order_item_str(sku, qty, is_last):
    if is_last:
        item_str = """{"product_sku": "%s", "quantity": %d} """ % (sku, qty)
    else:
        item_str = """{"product_sku": "%s", "quantity": %d}, """ % (sku, qty)
    return item_str


# get final items str for api data
def get_final_items_str(items_str):
    item_str_start = """ "items": [ """
    item_str_end = "], "
    final_items_str = item_str_start + items_str + item_str_end
    return final_items_str


# get ec order labels
def get_order_label_file_data(label_title):
    if label_title == "FOAEC":
        print()


# Test functions =====================================================
def run_create_order_api(data_dict):
    api_result = oms_api_call(customer_code="FPTEST", data_dict=data_dict)
    if api_result["result"]:
        response = api_result["json_response"]
        result_msg = response["ask"]
        if result_msg == "Success":
            content = {
                "result": True,
                "order_code": response["order_code"],
            }
        else:
            content = {
                "result": False,
                "msg": f"Error: {response['message']}"
            }
        print(content)
        # return content
    else:
        print(api_result)
        # return api_result


def test_f(**kwargs):
    for key, value in kwargs.items():
        print("{} is {}".format(key, value))

    import pandas as pd
    # list of strings
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)
    print(df)
    df_2 = df[df["col1"] == 1]
    print(df_2)
    df_3 = pd.DataFrame(columns=df.columns)
    for x, y in df.iterrows():
        df_3 = df_3.append(y)
        df_3.loc[x, "col3"] = 55
    print(df_3)


# test
def run_test():
    getOrderList_data_dict = {
        "service": "getOrderList",
        "paramsJson": """{
                "pageSize":1,
                "page":1,
                "order_code":"",
                "order_status":"",
                "shipping_method":"TEST_SELF_P1",
                "order_code_arr":[],
                "create_date_from":"2022-02-18",
                "create_date_to":"",
                "modify_date_from":"",
                "modify_date_to":"",
                "ship_date_from":"",
                "ship_date_to":""     
            }"""
    }

    item_str2 = """
    "items": [{"product_sku": "AEF-L138-BLK", "quantity": 1}, {"product_sku": "CM3246PC", "quantity": 1}], 
    """

    item_str_first = """ "items": [ """

    item_1 = "AEF-L138-BLK"
    item_1_qty = 1
    item_1_str = """{"product_sku": "%s", "quantity": %d}, """ % (item_1, item_1_qty)

    item_2 = "CM3246PC"
    item_2_qty = 1
    item_2_str = """{"product_sku": "%s", "quantity": %d} """ % (item_2, item_2_qty)

    item_str_end = "], "

    # item_str_final = item_str_first + item_1_str + item_2_str + item_str_end
    # print(item_str2)
    items_str = get_single_order_item_str(item_1, item_1_qty, False) + get_single_order_item_str(item_2, item_2_qty, True)
    item_str_final = get_final_items_str(items_str)
    # print(item_str_final)

    create_order_data_dict = {
        "service": "createOrder",
        "paramsJson": """{
            "warehouse_code": "FPWH1",
            "shipping_method": "TEST_SELF_P1",
            "reference_no": "FOAEC2203020005",
            "tracking_no": "FOAEC2203020005",
            "country_code": "US",
            "province": "CA",
            "city": "Yardley",
            "address1": "629 Remington Drive",
            "address2": "address2",
            "zipcode": "19067",
            "name": "ANDY TEST",
            "phone": "2153010403",
            "remark":"我是备注",
            %s
            "is_pack_box": 1,
            "verify": 1, 
            "label":{
                "file_type":"",
                "file_data":"",
                "file_size":""
            }
        }""" % item_str_final
    }
    # print(create_order_data_dict.get("paramsJson"))
    # run_create_order_api(create_order_data_dict)


# run_test()
# check_product_inventory("FPTEST", "CM3246PC123", "FPWH1")
# check_product_inventory("MTI", "MTI-311008003", "FURNITUREPROWH")


def createProduct(df, customer_api_key):
    settings = Settings(strict=False, xml_huge_tree=True)
    wsdl = 'http://oms.furnitureproslogistics.com/default/svc/wsdl'
    client = Client(wsdl, settings=settings)

    # using CFSFPL1 account API key
    data_dict = {
        "appToken": customer_api_key.get("appToken"),
        "appKey": customer_api_key.get("appKey"),
        "service": "createProduct",
    }

    product_map = {
        "WM90L-895HT": [800, 234, 234, 89],
        "TM90-1000": [1000, 224, 101, 224],
        "WM90L-1346HT": [1300, 229, 229, 135],
    }
    products = []  # To store valid products

    for index, row in df.iterrows():
        product_object = product_map.get(row["Item"])
        if not product_object:
            return {"status": "error", "message": f"Product Item {row['Item']} not found in product_map."}

        product = {
            "product_sku": row["BarCode"],
            "product_title": row["ContainerNo"] + "-" + row["Item"],
            "product_weight": product_object[0],
            "product_length": product_object[1],
            "product_width": product_object[2],
            "product_height": product_object[3],
            "product_declared_value": "1000",
            "product_declared_name": "roll",
            "verify": 1,
        }
        products.append(deepcopy(product))  # Collect product data for later API request

    for product in products:
        paramsJson = json.dumps(product)
        data_dict["paramsJson"] = paramsJson
        with client.settings(raw_response=True):
            response = client.service.callService(**data_dict)
            soup = BeautifulSoup(response.text, 'xml')
            ns1 = soup.find("ns1:callServiceResponse")
            if ns1:
                resp = ns1.find("response")
                if resp:
                    parsed = json.loads(resp.text)
                    # Log each product's API response
                    print(parsed)
                    if parsed.get("ask") != "Success":
                        error_message = parsed.get("Error", {}).get("errMessage")
                        return {"status": "error", "message": f"Error: {error_message}"}
                else:
                    error_message = parsed.get("Error", {}).get("errMessage")
                    return {"status": "error", "message": f"Error creating receiving order: {error_message}"}
            else:
                return {"status": "error", "message": "Service response not found in the server reply."}
    return {"status": "success", "message": "Products created successfully."}


def createReceivingOrder(df, customer_api_key):
    settings = Settings(strict=False, xml_huge_tree=True)
    wsdl = 'http://oms.furnitureproslogistics.com/default/svc/wsdl'
    client = Client(wsdl, settings=settings)

    # using CFSFPL1 account API key
    data_dict = {
        "appToken": customer_api_key.get("appToken"),
        "appKey": customer_api_key.get("appKey"),
        "service": "createAsn",
    }

    items = []
    for index, row in df.iterrows():
        item = {
            "product_sku": row["BarCode"],
            "quantity": 1,  # Adjust quantity based on your requirements
            "box_no": 1,  # Adjust box number based on your requirements
        }
        items.append(item)

    eta_time = datetime.now() + timedelta(days=1)
    eta_date = eta_time.strftime("%Y-%m-%d")
    paramsJson = {
        "reference_no": df.iloc[0]["ContainerNo"],  # Use the first row's ContainerNo as reference_no
        "warehouse_code": "FURNITUREPROWH",                 # Replace with appropriate warehouse code
        "tracking_number": df.iloc[0]["ContainerNo"],  # Use the first row's ContainerNo as tracking_number
        "eta_date": eta_date,  # Replace with appropriate ETA date
        "container_type": "40HQ",
        "items": items,
        "verify": 1,
    }

    data_dict["paramsJson"] = json.dumps(paramsJson)

    with client.settings(raw_response=True):
        response = client.service.callService(**data_dict)
        # print(response.text)

        soup = BeautifulSoup(response.text, 'xml')

        ns1 = soup.find("ns1:callServiceResponse")
        if ns1:
            resp = ns1.find("response")
            if resp:
                parsed = json.loads(resp.text)
                print(parsed)
                receiving_code = parsed.get("data", {}).get("receiving_code")
                if receiving_code:
                    return {"status": "success", "message": f"Receiving order {receiving_code} created successfully."}
                else:
                    error_message = parsed.get("Error", {}).get("errMessage")
                    return {"status": "error", "message": f"Error creating receiving order: {error_message}"}
            else:
                print("Response content not found.")
                return {"status": "error", "message": "Response content not found."}
        else:
            print("Service response not found.")
            return {"status": "error", "message": "Service response not found."}

