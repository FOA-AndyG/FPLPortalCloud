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

def get_ostk_po(conn):
    po_q = """SELECT * FROM po_sub_status WHERE status != 'X' order by status asc"""
    po_df = pd.read_sql_query(po_q, conn)
    po_df.replace([pd.NaT], [None])
    return list(po_df.itertuples(index=False))


def get_po_view(conn, receiving_code):
    #Master Ref	| SKU | Received | Total
    view_q = f"""SELECT master_ref_no, product_barcode, received, total FROM po_sub where receiving_code = '{receiving_code}'"""
    view_df = pd.read_sql_query(view_q, conn)
    view_df.replace([pd.NaT], [None])
    return list(view_df.itertuples(index=False)), len(view_df)
