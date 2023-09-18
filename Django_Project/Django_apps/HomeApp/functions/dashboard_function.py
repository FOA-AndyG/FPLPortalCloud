from calendar import monthrange
from datetime import datetime, timedelta

import pandas as pd

from Database.mysql_handler import SQLAlchemyHandler
from Django_apps.OMSOrderApp.reports.FPLContainerDash import get_container_report_function


def process_get_dashboard_data(date_type):

    with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi", password="A!05FOA2021edi") as db:
        content = get_orders_number(db, date_type)
        # total_container_df = get_container_number(db)
        # print(total_container_df)

    return content


def get_orders_number(db_handler, time_type):
    time_list = get_time_range(time_type)
    # print(time_list)
    # 4 = submit, 5 = 已打印, 6 = 已下架, 8 = 已出库
    # AND (o.order_status = 4 OR o.order_status = 5)
    # t.submit_time, t.process_time, t.ship_time
    content = {}
    try:
        total_sql = f"""
            SELECT COUNT(o.order_id) AS total_order
            FROM orders o
            LEFT JOIN order_operation_time t on o.order_id=t.order_id
            WHERE o.warehouse_id = 7
            AND o.order_status >= 4
            AND (t.submit_time >='{time_list[0]}' AND t.submit_time < '{time_list[1]}')
            """
        result_df = db_handler.read_sql_to_dataframe(total_sql)
        # print(result_df)
        content["total_orders"] = result_df['total_order'].iloc[0]

        new_sql = f"""
                SELECT COUNT(o.order_id) AS total_order
                FROM orders o
                LEFT JOIN order_operation_time t on o.order_id=t.order_id
                WHERE o.warehouse_id = 7
                AND o.order_status = 4
                AND (t.submit_time > '{time_list[0]}' AND t.submit_time < '{time_list[1]}')
                """
        # print(new_sql)
        result_df = db_handler.read_sql_to_dataframe(new_sql)
        # print(result_df)
        content["new_orders"] = result_df['total_order'].iloc[0]

        pending_sql = f"""
                SELECT COUNT(o.order_id) AS total_order
                FROM orders o
                LEFT JOIN order_operation_time t on o.order_id=t.order_id
                WHERE o.warehouse_id = 7
                AND (o.order_status = 5 OR o.order_status = 6)
                AND (t.process_time > '{time_list[0]}' AND t.process_time < '{time_list[1]}')
                """
        result_df = db_handler.read_sql_to_dataframe(pending_sql)
        # print(result_df)
        content["pending_orders"] = result_df['total_order'].iloc[0]

        shipped_sql = f"""
                   SELECT COUNT(o.order_id) AS total_order
                    FROM orders o
                    LEFT JOIN order_operation_time t on o.order_id=t.order_id
                    WHERE o.warehouse_id = 7
                    AND o.order_status = 8
                    AND (t.ship_time > '{time_list[0]}' AND t.ship_time < '{time_list[1]}')
                    """
        result_df = db_handler.read_sql_to_dataframe(shipped_sql)
        # print(result_df)
        content["shipped_orders"] = result_df['total_order'].iloc[0]

        content["time_type"] = time_type
        # print(int(content.get("shipped_orders") / content.get("total_orders")))
        # content["finish_percentage"] = int(int(content.get("shipped_orders")) / int(content.get("total_orders")))

    except Exception as e:
        print("get_orders_number:", e)

    # print(content)
    return content


def get_container_number(db_handler):
    # 5 = on the way: upcoming containers
    # AND (r.expected_date > '2022-04-25' AND r.expected_date < '2022-05-02')
    try:
        base_sql = f"""
            SELECT customer_code, count(customer_code) as Inbound
            FROM receiving r
            WHERE r.warehouse_id = 7
            AND receiving_status = 5
            AND receiving_code like 'RV%%'
            GROUP BY customer_code
            """
        result_df = db_handler.read_sql_to_dataframe(base_sql)
        print(result_df)
        return result_df
    except Exception as e:
        print("get_container_number:", e)
        return pd.DataFrame()


def get_container_received(db_handler, time_list):
    # 6 and 7 = put the way: how many containers we received

    try:
        base_sql = f"""
            SELECT r.customer_code, COUNT(r.customer_code) as Inbound
            FROM receiving r
            LEFT JOIN putaway p
            ON r.receiving_code = p.receiving_code
            WHERE r.warehouse_id = 7
            AND (r.receiving_status = 6 OR r.receiving_status = 7)
            AND r.receiving_code like 'RV%%'
            AND (p.putaway_update_time > '{time_list[0]}' OR p.putaway_update_time > '{time_list[1]}')
            GROUP BY r.customer_code
            """
        result_df = db_handler.read_sql_to_dataframe(base_sql)
        print(result_df)
        return result_df
    except Exception as e:
        print("get_container_received:", e)
        return pd.DataFrame()


def get_time_range(range_type) -> []:
    current_time = datetime.now()
    current_year = current_time.year
    current_month = current_time.month
    num_days = monthrange(current_year, current_month)[1]

    range_dict = {
        "Daily": [
            datetime.strftime(current_time, '%Y-%m-%d'),
            datetime.strftime(current_time + timedelta(days=1), '%Y-%m-%d'),
            datetime.strftime(current_time, '%Y-%m-%d'),
        ],

        "Weekly": [
            datetime.strftime(current_time - timedelta(days=7), '%Y-%m-%d'),
            datetime.strftime(current_time + timedelta(days=1), '%Y-%m-%d'),
            datetime.strftime(current_time, '%Y-%m-%d'),
        ],

        "Monthly": [
            f"{current_year}-{current_month}-01",
            f"{current_year}-{current_month}-{num_days}",
            datetime.strftime(current_time, '%B')
        ],

        "Yearly": [
            f"{current_year}-01-01",
            f"{current_year+1}-01-01",
            current_year
        ]
    }
    return range_dict.get(range_type)


def process_get_container_data():
    time_list = get_time_range("Daily")
    response_data = None
    received_response_data = None
    with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                           password="A!05FOA2021edi") as db:
        total_container_df = get_container_number(db)
        # today_container_received = get_container_received(db, time_list)

    if not total_container_df.empty:
        data = []
        labels = []
        total_container = 0
        for index, row in total_container_df.iterrows():
            labels.append(row[0])
            data.append(row[1])
            total_container += int(row[1])
        response_data = {
            "result": True,
            "msg": "Success",
            "data": data,
            "labels": labels,
            "total_container": total_container
        }
    else:
        response_data = {
            "result": False,
            "msg": "No data",
        }
    # if not today_container_received.empty:
    #     print("today_container_received.empty")
    #     received_data = []
    #     received_labels = []
    #     total_received_container = 0
    #     for index, row in today_container_received.iterrows():
    #         received_labels.append(row[0])
    #         received_data.append(row[1])
    #         total_received_container += int(row[1])
    #     received_response_data = {
    #         "received_result": True,
    #         "received_msg": "Success",
    #         "received_data": received_data,
    #         "received_labels": received_labels,
    #         "total_received_container": total_received_container,
    #         "current_day": time_list[0]
    #     }
    # response_data.update(received_response_data)
    return response_data


def process_inventory_remaining_data():
    df = get_container_report_function()
    df.columns = ["", "Inbound(Today)", "Inventory(Total)", "Outbound(Today)"]
    # "df_columns": ['customer_code', 'Inbound', 'Inventory', 'Outbound']
    if not df.empty:
        inbound_data = []
        outbound_data = []
        inventory_data = []
        labels = []
        for index, row in df.iterrows():
            if index != "total":
                print()

    else:
        response_data = {
            "result": False,
            "msg": "No data",
        }
    return response_data
