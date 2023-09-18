import json
import re
from datetime import datetime

import pandas
from channels.generic.websocket import WebsocketConsumer

from Database.mysql_handler import ECANGMySQLConnection
from Django_apps.ScanApp.models import Containerlog, Containerlogerror


class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.check_carrier = {
            "1Z": "UPS",
            "96": "FEDEX",
            "42": "USPS",   # 420770189305510923030833722030
            "10": "FEDEX",  # FedEx next day
            "FO": "WH03",
            "TB": "AMXL",
            "D1": "ONTRACK"
        }
        try:
            with ECANGMySQLConnection() as db:
                sql = """
                SELECT o.order_code
                , o.order_status
                , p.product_barcode
                , o.parcel_quantity
                , s.tracking_number
                , oa.multiple_tracking_number
                from orders o
                LEFT JOIN picking_detail AS p ON o.order_id = p.order_id
                LEFT JOIN ship_order s ON o.order_id=s.order_id
                LEFT JOIN order_additional AS oa ON o.order_id = oa.order_id
                WHERE o.warehouse_id in (7,8)
                AND o.order_status IN (5,6,7)
                """
                self.df = db.read_sql_to_dataframe(sql)
                self.df['tracking_number'] = self.df['tracking_number'].astype(str)
                self.df["tracking_number"] = self.df["tracking_number"].str.replace(' ', '')
                # print(self.df.head(5))
        except Exception as e:
            print(e)
            self.df = pandas.DataFrame()

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["trailer_number"]
        print(self.room_name)
        self.accept()
        print("socket is connected..")
        # self.conn.__enter__()

    def disconnect(self, close_code):
        print("socket is closed..")
        # self.conn.__exit__("Close", "database connection closed", "")
        pass

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            trailer = str(text_data_json["trailer"]).upper()
            message = str(text_data_json["message"]).upper()
            username = text_data_json["username"]
            isCheck = text_data_json["isCheck"]

            print(trailer, message)
            # check scan tracking to see which carrier
            label_tracking = ""
            try:
                carrier = self.check_carrier.get(message[:2])
                if carrier == "FEDEX" or carrier == "USPS":
                    label_tracking = message[-12:]
            except Exception as e:
                carrier = "Unknown"

            if carrier not in trailer:
                result_signal = False
            else:
                result_signal = True

            result_content = {
                "result_signal": result_signal,
                "message": f"Error: loading wrong box into the trailer"
            }
            print(username, trailer, carrier, message, label_tracking, result_signal, isCheck)
            current_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            if result_content["result_signal"]:
                # TODO: check if the tracking exists in internal database
                exist_records = Containerlog.objects.using('mssql167').filter(tracking=message)
                # print(exist_records)
                if exist_records.exists():
                    result_content = {
                        "result_signal": False,
                        "message": f"Error: [{message}] has been scanned!"
                    }
                    error_scan_record = Containerlogerror.objects.using('mssql167').create(containerno=trailer,
                                                                                           carrier=carrier,
                                                                                           tracking=message,
                                                                                           createdate=current_time,
                                                                                           machinename=username,
                                                                                           note=result_content["message"])
                    error_scan_record.save()
                else:
                    # not exist in the internal database, keep process the tracking
                    if label_tracking:
                        check_tracking = label_tracking
                        result_content["message"] += f"={check_tracking}"
                    else:
                        check_tracking = message
                    # TODO: check if the tracking exists in EC database
                    if isCheck == "true":
                        # 1. check another tracking_number column
                        row = self.df[self.df['tracking_number'].str.contains(check_tracking)]
                        if not row.empty:
                            print(row)
                            # save the record into internal database
                            result_content = {
                                "result_signal": True,
                                "message": f"Success: [{current_time}] {carrier}={message}={row['order_code'].iloc[0]}"
                            }
                            new_scan_record = Containerlog.objects.using('mssql167').create(containerno=trailer,
                                                                                            carrier=carrier,
                                                                                            tracking=message,
                                                                                            createdate=current_time,
                                                                                            machinename=username,
                                                                                            order_code=row["order_code"].iloc[0],
                                                                                            product_code=row["product_barcode"].iloc[0])
                            new_scan_record.save()
                        else:
                            # 2. check another multiple_tracking_number column
                            row = self.df[self.df['multiple_tracking_number'].str.contains(check_tracking)]
                            if not row.empty:
                                print(row)
                                # save the record into internal database
                                result_content = {
                                    "result_signal": True,
                                    "message": f"Success: [{current_time}] {carrier}={message}={row['order_code'].iloc[0]}"
                                }
                                new_scan_record = Containerlog.objects.using('mssql167')\
                                    .create(containerno=trailer, carrier=carrier, tracking=message,
                                            createdate=current_time, machinename=username,
                                            order_code=row["order_code"].iloc[0],
                                            product_code=row["product_barcode"].iloc[0])
                                new_scan_record.save()
                            else:
                                result_content = {
                                    "result_signal": False,
                                    "message": f"Error: [{current_time}] {carrier}={message}=Not found in the system"
                                }
                                error_scan_record = Containerlogerror.objects.using('mssql167')\
                                    .create(containerno=trailer, carrier=carrier, tracking=message,
                                            createdate=current_time, machinename=username, note=result_content["message"])
                                error_scan_record.save()
                    else:
                        # not check with WMS, just save record into the internal database
                        result_content = {
                            "result_signal": True,
                            "message": f"Success: [{current_time}] {carrier}={message}"
                        }
                        new_scan_record = Containerlog.objects.using('mssql167').create(containerno=trailer,
                                                                                        carrier=carrier,
                                                                                        tracking=message,
                                                                                        createdate=current_time,
                                                                                        machinename=username)
                        new_scan_record.save()
            else:
                # load wrong trailer error
                error_scan_record = Containerlogerror.objects.using('mssql167').create(containerno=trailer,
                                                                                       carrier=carrier,
                                                                                       tracking=message,
                                                                                       createdate=current_time,
                                                                                       machinename=username,
                                                                                       note=result_content["message"])
                error_scan_record.save()
        except Exception as e:
            result_content = {
                "result_signal": False,
                "message": f"Error: {e}, please contact IT"
            }

        # send result back to front end
        self.send(text_data=json.dumps(result_content))
