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
from .sql_connection import *

# def mysql_connection():
#     conn = pymysql.connect(
#         host='35.225.128.227', # prod
#         # host='34.71.96.24',  # testing
#         user='prog',
#         password="Prog@123",
#         db='ostk_fpl',
#     )
#     return conn


# def cloud_connection():
#     conn = pymysql.connect(
#         host='35.208.191.39',
#         user='vincentlee',
#         password="Prog@123",
#         db='itweb',
#     )
#     return conn


# def wms_mysql_connection():
#     connwms = pymysql.connect(
#         host='34.96.174.105',
#         user='edi',
#         password="A!05FOA2021edi",
#         db='wms',
#     )
#     return connwms

def lax_ostk_inv(conn):
    cursor = conn.cursor()
    inv_q = """SELECT u.product_barcode, u.product_title, i.pi_sellable, i.pi_reserved, i.pi_shipped, r.received AS received FROM product AS u
    LEFT JOIN product_inventory AS i ON u.product_barcode = i.product_barcode
    LEFT JOIN (SELECT product_barcode, SUM(pil_quantity) AS received FROM product_inventory_log WHERE warehouse_id = 7 AND application_code = 'Putaway' GROUP BY product_barcode) AS r ON r.product_barcode = u.product_barcode
    WHERE i.customer_code = 'OSTK' AND i.warehouse_id = 7 AND NOT i.product_barcode = 'OSTK-TESTSKU1'"""
    cursor.execute(inv_q)
    data = cursor.fetchall()
    cursor.close()
    return data

def tx_ostk_inv(conn):
    cursor = conn.cursor()
    inv_q = """SELECT u.product_barcode, u.product_title, i.pi_sellable, i.pi_reserved, i.pi_shipped, r.received AS received FROM product AS u
    LEFT JOIN product_inventory AS i ON u.product_barcode = i.product_barcode
    LEFT JOIN (SELECT product_barcode, SUM(pil_quantity) AS received FROM product_inventory_log WHERE warehouse_id = 11 AND application_code = 'Putaway' GROUP BY product_barcode) AS r ON r.product_barcode = u.product_barcode
    WHERE i.customer_code = 'OSTK' AND i.warehouse_id = 11 AND NOT i.product_barcode = 'OSTK-TESTSKU1'"""
    cursor.execute(inv_q)
    data = cursor.fetchall()
    cursor.close()
    return data