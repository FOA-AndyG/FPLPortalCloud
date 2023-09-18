import json
from datetime import datetime

from channels.generic.websocket import WebsocketConsumer

from Database.mysql_handler import ECANGMySQLConnection
from Django_apps.ScanApp.models import Containerlog


class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.conn = ECANGMySQLConnection()

    def connect(self):
        self.accept()
        print("socket is connected..")
        self.conn.__enter__()

    def disconnect(self, close_code):
        print("socket is closed..")
        self.conn.__exit__("Close", "database connection closed", "")
        pass

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            trailer = text_data_json["trailer"]
            message = text_data_json["message"]
            username = text_data_json["username"]
            isCheck = text_data_json["isCheck"]

            # check scan tracking to see which carrier
            label_tracking = ""
            carrier = "Unknown"
            if str(message).startswith('1Z') or str(message).startswith('1z'):
                carrier = "UPS"
            if str(message).startswith('96'):
                carrier = "FEDEX"
                label_tracking = str(message)[-12:]
            if str(message).startswith('TBA') or str(message).startswith('tba'):
                carrier = "AMXL"
            if str(message).startswith('D1') or str(message).startswith('d1'):
                carrier = "ONTRACK"

            if carrier not in trailer:
                result_signal = "Error"
            else:
                result_signal = "Success"

            print(username, trailer, carrier, message, label_tracking, result_signal, isCheck)
            current_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

            # TODO: check if the tracking exists in internal database
            try:
                exist_record = Containerlog.objects.using('mssql167').get(tracking=message)
                result_content = {
                    "result_signal": "Error",
                    "message": f"Error: [{message}] has been scanned!"
                }
                self.send(text_data=json.dumps(result_content))

            except Exception as e:
                # save the record into internal database
                new_scan_record = Containerlog.objects.using('mssql167').create(containerno=trailer,
                                                                                carrier=carrier, tracking=message,
                                                                                createdate=current_time,
                                                                                machinename=username)
                new_scan_record.save()

                result_content = {
                    "result_signal": result_signal,
                    "message": f"{result_signal}|[{current_time}]: {carrier}={message}"
                }

                if label_tracking:
                    check_tracking = label_tracking
                    result_content["message"] += f"={check_tracking}"
                else:
                    check_tracking = message

                # TODO: check if the tracking exists in EC database
                if isCheck == "true":
                    test_sql = f"""
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
                                    WHERE o.warehouse_id=7
                                    AND o.order_status IN (5,6,7)
                                    AND s.tracking_number = '{check_tracking}'
                                    """

                    check_sql = f"""
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
                    WHERE o.warehouse_id=7
                    AND o.order_status IN (5,6,7)
                    AND (s.tracking_number LIKE '%393611922123%' OR oa.multiple_tracking_number LIKE '%393611922123%')
                    """
                    check_df = self.conn._conn.execute(test_sql).fetchone()
                    print(check_df)

                    if not check_df["order_code"]:
                        result_content["result_signal"] = "Error"
                        result_content["message"] = f"Error|[{current_time}]: {carrier}={message}={check_tracking}=Not found in the system"
                    else:
                        result_content["message"] += f"={check_df['order_code']}={check_df['product_barcode']}"

                # send result back to front end
                self.send(text_data=json.dumps(result_content))

        except Exception as e:
            result_content = {
                "result_signal": "Error",
                "message": f"Error: {e}, please contact IT"
            }
            self.send(text_data=json.dumps(result_content))
