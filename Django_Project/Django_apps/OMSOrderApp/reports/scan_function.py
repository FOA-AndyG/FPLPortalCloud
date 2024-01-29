import os
from datetime import datetime

import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

from Database.mysql_handler import SQLAlchemyHandler
from Django_apps.OMSOrderApp.export_function.download_attachment import get_picking_details_df, get_picking_list


# functions for compare tracking =====================================
def return_match_tracking_function(db, picking, scan_df):
    picking_dict = get_picking_details_df(db, picking)
    if picking_dict["result"]:
        picking_df = picking_dict["result_df"]
        picking_df = picking_df.fillna('')
        picking_df['tracking_number'] = picking_df['tracking_number'].astype(str)
        picking_df["tracking_number"] = picking_df["tracking_number"].str.replace(' ', '')
        picking_df["tracking_number"] = picking_df["tracking_number"].str.replace('&AMP;', ',')
        picking_df["tracking_number"] = picking_df["tracking_number"].str.replace('&amp;', ',')
        picking_df["tracking_number"] = picking_df["tracking_number"].str.replace('&', ',')

        picking_df = picking_df.assign(tracking_number=picking_df.tracking_number.str.split(",")).explode("tracking_number")

        picking_df["multiple_tracking_number"] = picking_df["multiple_tracking_number"].str.replace(' ', '')
        picking_df["multiple_tracking_number"] = picking_df["multiple_tracking_number"].str.replace('&AMP;', ',')
        picking_df["multiple_tracking_number"] = picking_df["multiple_tracking_number"].str.replace('&amp;', ',')
        picking_df["multiple_tracking_number"] = picking_df["multiple_tracking_number"].str.replace('&', ',')

        picking_df = picking_df.assign(
            multiple_tracking_number=picking_df.multiple_tracking_number.str.split(",")).explode(
            "multiple_tracking_number")

        picking_df['tracking_number'] += picking_df["multiple_tracking_number"]

        picking_df = picking_df.merge(scan_df, how="left",
                                      left_on="tracking_number",
                                      right_on="Tracking")
        picking_df["TrackingCheck"] = picking_df.apply(lambda row: tracking_categorise(row), axis=1)

        return picking_df
    else:
        return pd.DataFrame()


def tracking_categorise(row):
    if row["Carrier"] == "FEDEX":
        tracking_url = f"https://www.fedex.com/fedextrack/?trknbr={row['Tracking']}"
    elif row["Carrier"] == "UPS":
        tracking_url = f"https://wwwapps.ups.com/WebTracking/track?track=yes&trackNums={row['Tracking']}"
    else:
        tracking_url = ""
    return tracking_url


# functions for compare tracking with no shipped orders =====================================

def return_match_tracking_function_no_shipped_orders(db, picking, scan_df):
    picking_dict = get_picking_details_df_no_shipped_orders(db, picking)
    if picking_dict["result"]:
        picking_df = picking_dict["result_df"]
        picking_df = picking_df.fillna('')
        picking_df['tracking_number'] = picking_df['tracking_number'].astype(str)
        picking_df["tracking_number"] = picking_df["tracking_number"].str.replace(' ', '')
        picking_df["tracking_number"] = picking_df["tracking_number"].str.replace('&AMP;', ',')
        picking_df["tracking_number"] = picking_df["tracking_number"].str.replace('&amp;', ',')
        picking_df["tracking_number"] = picking_df["tracking_number"].str.replace('&', ',')

        picking_df = picking_df.assign(tracking_number=picking_df.tracking_number.str.split(",")).explode(
            "tracking_number")

        picking_df["multiple_tracking_number"] = picking_df["multiple_tracking_number"].str.replace(' ', '')
        picking_df["multiple_tracking_number"] = picking_df["multiple_tracking_number"].str.replace('&AMP;', ',')
        picking_df["multiple_tracking_number"] = picking_df["multiple_tracking_number"].str.replace('&amp;', ',')
        picking_df["multiple_tracking_number"] = picking_df["multiple_tracking_number"].str.replace('&', ',')

        picking_df = picking_df.assign(multiple_tracking_number=picking_df.multiple_tracking_number.str.split(",")).explode(
            "multiple_tracking_number")

        picking_df['tracking_number'] += picking_df["multiple_tracking_number"]

        picking_df = picking_df.merge(scan_df, how="left", left_on="tracking_number", right_on="Tracking")
        picking_df["TrackingCheck"] = picking_df.apply(lambda row: tracking_categorise(row), axis=1)
        return picking_df
    else:
        return pd.DataFrame()


def get_picking_details_df_no_shipped_orders(db, picking):
    try:
        base_sql = f"""
        SELECT p.picking_code, p.order_code, p.lc_code, p.product_barcode, o.order_status
        ,p.pd_quantity
        ,o.reference_no
        ,s.tracking_number
        ,oa.multiple_tracking_number
        ,o.sm_code
        ,b.oab_firstname
        ,b.oab_postcode
        ,b.oab_state
        ,b.oab_city
        ,b.oab_street_address1
        ,o.remark
        FROM picking_detail as p
        LEFT JOIN orders as o ON p.order_id = o.order_id
        LEFT JOIN order_additional AS oa ON p.order_id = oa.order_id
        LEFT JOIN order_attached AS a ON p.order_id = a.order_id
        LEFT JOIN order_pack_detail as pd ON p.order_code = pd.order_code AND p.product_barcode = pd.product_barcode
        LEFT JOIN order_address_book AS b ON p.order_id = b.order_id
        LEFT JOIN ship_order AS s ON p.order_id = s.order_id
        WHERE p.picking_code = '{picking}' AND o.order_status != 8
        GROUP BY p.order_code, p.product_barcode, pd.box_num
        ORDER BY p.pick_sort, p.lc_code, p.product_barcode, p.order_code asc
        """
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

# ==========================================================================
