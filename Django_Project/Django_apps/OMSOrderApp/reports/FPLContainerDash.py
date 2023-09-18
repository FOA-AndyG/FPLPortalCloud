import pandas

from Database.mysql_handler import SQLAlchemyHandler


def get_container_report_function():
    try:
        from sqlalchemy import create_engine
        engine = "mysql+pymysql"
        ip_address = "34.96.174.105"
        database_name = "wms"
        user = "edi"
        password = "A!05FOA2021edi"
        conn = create_engine(f'{engine}://{user}:{password}@{ip_address}/{database_name}')

        inventory = pandas.read_sql("""
        SELECT inv.customer_code, inv.product_barcode, sum(inv.pi_sellable) AS pi_sellable, p.product_length, p.product_width, p.product_height 
        FROM product_inventory inv 
        LEFT JOIN product p on inv.product_barcode=p.product_barcode
        WHERE inv.warehouse_id=7
        GROUP BY inv.customer_code, inv.product_barcode, p.product_length, p.product_width, p.product_height
        """, conn)
        inventory['item_volume'] = inventory[['pi_sellable', 'product_length', 'product_width', 'product_height']].prod(
            axis=1) / 28316.8  # convert to ft3
        inventory_volume = inventory.groupby(['customer_code'])['item_volume'].sum() / 2300
        inventory_volume = inventory_volume.to_frame().reset_index()
        inventory_volume.columns = ['customer_code', 'Inventory']
        # print(inventory_volume)

        inbound = pandas.read_sql("""
        SELECT r.customer_code, COUNT(r.customer_code) as Inbound
        FROM receiving r
        LEFT JOIN putaway p
        ON r.receiving_code = p.receiving_code
        
        WHERE r.warehouse_id = 7
        AND (r.receiving_status = 6 OR r.receiving_status = 7)
        AND r.receiving_code like 'RV%%'
        AND p.putaway_update_time >= date(convert_tz(now(),@@session.time_zone,'-08:00'))
        GROUP BY r.customer_code
        """, conn)
        # print(inbound)

        outbound = pandas.read_sql("""
        SELECT o.customer_code, op.product_barcode, o.order_code, p.product_length,
         p.product_width, p.product_height, op.op_quantity, t.process_time
        FROM orders o
        LEFT JOIN order_product op ON o.order_id=op.order_id
        LEFT JOIN product p on op.product_barcode=p.product_barcode
        LEFT JOIN order_operation_time t on o.order_id=t.order_id
        WHERE t.ship_time>=date(convert_tz(now(),@@session.time_zone,'-08:00'))
        """, conn)  # WHERE date(o.update_time) = CURDATE() AND o.order_status=8
        outbound['item_volume'] = outbound[['op_quantity', 'product_length', 'product_width', 'product_height']].prod(axis=1) / 28316.8  # convert to ft3
        outbound_volume = outbound.groupby(['customer_code'])['item_volume'].sum() / 2300
        outbound_volume = outbound_volume.to_frame().reset_index()
        outbound_volume.columns = ['customer_code', 'Outbound']
        # print(outbound_volume)

        will_outbound = pandas.read_sql("""
        SELECT o.customer_code, op.product_barcode, o.order_code, p.product_length,
         p.product_width, p.product_height, op.op_quantity, t.process_time
        FROM orders o
        LEFT JOIN order_product op ON o.order_id=op.order_id
        LEFT JOIN product p on op.product_barcode=p.product_barcode
        LEFT JOIN order_operation_time t on o.order_id=t.order_id
        WHERE o.warehouse_id = 7
		AND (o.order_status = 5 OR o.order_status = 7)
        """, conn)
        will_outbound['item_volume'] = will_outbound[['op_quantity', 'product_length', 'product_width', 'product_height']].prod(axis=1) / 28316.8  # convert to ft3
        will_outbound_volume = will_outbound.groupby(['customer_code'])['item_volume'].sum() / 2300
        will_outbound_volume = will_outbound_volume.to_frame().reset_index()
        will_outbound_volume.columns = ['customer_code', 'WillOutbound']

        final = inventory_volume.merge(inbound, how='left').merge(outbound_volume, how='left').merge(will_outbound_volume, how='left').fillna(0)
        final = final.round(decimals=3)
        final = final[['customer_code', 'Inbound', 'Inventory', 'Outbound', 'WillOutbound']]
        final.loc["total"] = final.sum(numeric_only=True)
        final = final.fillna('')
        # print(final)
        return final
    except Exception as e:
        print("get_container_report_function: ", e)
        return pandas.DataFrame()


def get_container_report_function_new():
    try:
        with SQLAlchemyHandler(ip_address="34.96.174.105", database_name="wms", user="edi",
                               password="A!05FOA2021edi") as db:
            inventory_sql = """
                SELECT inv.customer_code, inv.product_id, inv.product_barcode, 
                inv.pi_sellable, inv.pi_reserved, inv.pi_onway, inv.pi_shipped,
                p.product_length, p.product_width, p.product_height
                FROM wms.product_inventory as inv 
                LEFT JOIN wms.product_warehouse_attribute AS p
                ON inv.product_id = p.product_id
                WHERE inv.warehouse_id=7
            """
            inventory_df = db.read_sql_to_dataframe(inventory_sql)

            inventory_df["Inventory_Remain"] = ((inventory_df["product_length"] * inventory_df["product_width"] * inventory_df["product_height"])/28316.8) * inventory_df["pi_sellable"]
            inventory_df["Will_Outbound"] = ((inventory_df["product_length"] * inventory_df["product_width"] * inventory_df["product_height"])/28316.8) * inventory_df["pi_reserved"]
            inventory_df["Will_Inbound"] = ((inventory_df["product_length"] * inventory_df["product_width"] * inventory_df["product_height"])/28316.8) * inventory_df["pi_onway"]

            inventory_volume = inventory_df.groupby(['customer_code'])['Inventory_Remain'].sum() / 2350
            inventory_volume = inventory_volume.to_frame().reset_index()
            inventory_volume.columns = ['customer_code', 'Inventory_Remain']

            will_outbound_volume = inventory_df.groupby(['customer_code'])['Will_Outbound'].sum() / 2350
            will_outbound_volume = will_outbound_volume.to_frame().reset_index()
            will_outbound_volume.columns = ['customer_code', 'Will_Outbound']

            will_inbound_volume = inventory_df.groupby(['customer_code'])['Will_Inbound'].sum() / 2350
            will_inbound_volume = will_inbound_volume.to_frame().reset_index()
            will_inbound_volume.columns = ['customer_code', 'Will_Inbound']

            final = inventory_volume.merge(will_outbound_volume, how='left').merge(will_inbound_volume, how='left').fillna(0)
            final = final.round(decimals=2)
            final.loc["total"] = final.sum(numeric_only=True)
            final = final.fillna('')
            # print(final)

            return final
    except Exception as e:
        print("get_container_report_function_new: ", e)
        return pandas.DataFrame()


def get_container_report_by_date(request):
    print()
