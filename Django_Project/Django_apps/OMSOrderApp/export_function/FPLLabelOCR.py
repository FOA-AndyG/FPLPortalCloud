import pandas
import pymysql
import mysql.connector as connection
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import pysftp
import os

def GetLabel(row):
    HOSTNAME = "34.96.174.105"
    USERNAME = "eccang"
    PASSWORD = "eccang123"
    KEY_PATH = "C:/Users/kaheil/Downloads/eccang"

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    sftp = pysftp.Connection(HOSTNAME, username=USERNAME, private_key=KEY_PATH, private_key_pass=PASSWORD, cnopts=cnopts)
    sftp.get('/data/www/trunk/oms'+row['oat_file_path'])
    file=os.path.basename(row['oat_file_path'])

    OK=CheckLabel(row, file)
    return OK

def LabelOCR(file):
    #print(file)
    text_arr=[]
    pdf = convert_from_path(file,200, poppler_path = r"C:\Program Files\poppler-22.01.0\Library\bin")
    path, fileName = os.path.split(file)
    fileBaseName, fileExtension = os.path.splitext(fileName)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    for page_number, page_data in enumerate(pdf):
        print('Page :'+ str(page_number))
        text = pytesseract.image_to_string(page_data).upper()#.encode("utf-8")
        print(text)
        text_arr.append(text)
    return text_arr

def CheckLabel(row,file):
    text_arr = LabelOCR(file)
    OK=True
    if not (any(row['product_sku'].upper() in string for string in text_arr)):
        OK = False
    if not (any(row['oab_firstname'].upper() in string for string in text_arr)):
        OK = False
    return OK

conn = connection.connect(host="34.96.174.105", database='wms', user="edi", passwd="A!05FOA2021edi", port=3306)
orders = pandas.read_sql("""SELECT orders.order_id, orders.order_code, orders.order_status, orders.reference_no,product.product_sku, order_attached.oat_file_path,order_address_book.oab_firstname, order_address_book.oab_postcode,order_address_book.oab_state,order_address_book.oab_city,order_address_book.oab_street_address1, order_address_book.oab_street_address2 FROM wms.orders 
                    LEFT JOIN wms.order_product ON wms.order_product.order_id=wms.orders.order_id
                    LEFT JOIN wms.order_attached ON wms.order_attached.order_id=wms.orders.order_id
                    LEFT JOIN wms.order_address_book ON wms.order_address_book.order_id=wms.orders.order_id
                    LEFT JOIN wms.product ON wms.order_product.product_id=wms.product.product_id
                    WHERE orders.order_status>=3 AND oat_file_path IS NOT null""", conn)
for index, row in orders.iterrows():
    print(row['order_code']+str(GetLabel(row)))
    print ('..................')