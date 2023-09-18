import pandas as pd
from Database.mysql_handler import SQLAlchemyHandler


def get_container_info_list():
    # receiving_status: 0 = delete, 5 = on the way, 6 = receiving, 7 = receiving finished, 8 = put away finished
    print()


def get_container_report():
    will_send_sql = """
    SELECT o.customer_code, op.product_barcode, o.order_code, p.product_length,
    p.product_width, p.product_height, op.op_quantity
    FROM orders o
    LEFT JOIN order_product op ON o.order_id=op.order_id
    LEFT JOIN product p on op.product_barcode=p.product_barcode
    WHERE o.warehouse_id = 7
    AND (o.order_status = 5 OR o.order_status = 7)
    """
    with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                           password="A!05FOA2021edi") as db:
        will_send_df = db.read_sql_to_dataframe(will_send_sql)



