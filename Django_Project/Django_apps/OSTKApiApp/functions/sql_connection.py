import pymysql


def mysql_connection():
    conn = pymysql.connect(
        host='35.225.128.227', # prod
        # host='34.71.96.24',  # testing
        user='prog',
        password="Prog@123",
        db='ostk_fpl',
    )
    return conn


def cloud_connection():
    conn = pymysql.connect(
        host='35.208.191.39',
        user='vincentlee',
        password="Prog@123",
        db='itweb',
    )
    return conn


def wms_mysql_connection():
    connwms = pymysql.connect(
        host='34.96.174.105',
        user='edi',
        password="A!05FOA2021edi",
        db='wms',
    )
    return connwms