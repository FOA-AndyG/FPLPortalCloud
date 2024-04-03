import json
import pymysql
import datetime
from datetime import timedelta
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
from django.contrib import messages
import pytz
import numpy as np
from io import BytesIO
from django.http import HttpResponse
import re
import openpyxl
import os
from Django_Project.settings import STATICFILES_DIRS
import xlrd
import xlwt
from xlutils.copy import copy

# def get_ostk_po(conn):
#     po_q = """SELECT * FROM po_sub_status WHERE status != 'X' order by status asc"""
#     po_df = pd.read_sql_query(po_q, conn)
#     po_df.replace([pd.NaT], [None])
#     return list(po_df.itertuples(index=False))

def get_ostk_po(conn):
    po_q = """SELECT receiving_code, wh_code, master_ref_no, 
    COUNT(product_barcode) as num_products, SUM(received) as received, SUM(total) as total, MAX(update_time) as update_time, MAX(status) as status
    FROM ostk_fpl.po_sub
    WHERE status <> 'X' AND (wh_code = 'FPLTX1' OR wh_code = 'FURNITUREPROWH')
    GROUP BY master_ref_no
    order by receiving_code desc"""
    po_df = pd.read_sql_query(po_q, conn)
    po_df.replace([pd.NaT], [None])
    return list(po_df.itertuples(index=False))


def get_po_view(conn, receiving_code):
    #Master Ref	| SKU | Received | Total
    view_q = f"""SELECT master_ref_no, product_barcode, received, total FROM po_sub where receiving_code = '{receiving_code}'"""
    view_df = pd.read_sql_query(view_q, conn)
    view_df.replace([pd.NaT], [None])
    return list(view_df.itertuples(index=False)), len(view_df)

def get_ref_view(conn, master_ref_no):
    #Master Ref	| SKU | Received | Total
    view_q = f"""SELECT product_barcode, received, total FROM po_sub where master_ref_no = '{master_ref_no}'"""
    view_df = pd.read_sql_query(view_q, conn)
    view_df.replace([pd.NaT], [None])
    return list(view_df.itertuples(index=False)), len(view_df)