from django.db import models


# Create your models here.
class OmsOrderImportBatch(models.Model):
    batch_id = models.IntegerField(blank=True, null=True)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    warehouse_code = models.CharField(max_length=100, blank=True, null=True)
    reference_code = models.CharField(max_length=100, blank=True, null=True)
    delivery_method = models.CharField(max_length=45, blank=True, null=True)
    sales_platform = models.CharField(max_length=45, blank=True, null=True)
    customer_code = models.CharField(max_length=45, blank=True, null=True)
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    label_tracking_number = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    consignee_name = models.CharField(max_length=100, blank=True, null=True)
    consignee_company = models.CharField(max_length=100, blank=True, null=True)
    consignee_country = models.CharField(max_length=45, blank=True, null=True)
    consignee_state = models.CharField(max_length=45, blank=True, null=True)
    consignee_city = models.CharField(max_length=100, blank=True, null=True)
    consignee_street = models.CharField(max_length=255, blank=True, null=True)
    consignee_street2 = models.CharField(max_length=255, blank=True, null=True)
    consignee_zipcode = models.CharField(max_length=45, blank=True, null=True)
    consignee_email = models.CharField(max_length=155, blank=True, null=True)
    consignee_phone = models.CharField(max_length=45, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    is_order_box = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=45, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    attach_path = models.CharField(max_length=255, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'oms_order_import_batch'


class OmsOrderProductImportBatch(models.Model):
    batch_id = models.IntegerField(blank=True, null=True)
    order_id = models.CharField(max_length=155, blank=True, null=True)
    customer_code = models.CharField(max_length=45, blank=True, null=True)
    sku = models.CharField(max_length=155, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    ec_sku = models.CharField(max_length=155, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'oms_order_product_import_batch'


class OmsLabelDownloadTime(models.Model):
    picking_number = models.CharField(max_length=45, blank=True, null=True)
    username = models.CharField(max_length=45, blank=True, null=True)
    download_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'oms_label_download_time'


class Product(models.Model):
    product_id = models.IntegerField(primary_key=True)
    product_sku = models.TextField(blank=True, null=True)
    product_barcode = models.TextField(blank=True, null=True)
    goods_barcode = models.TextField(blank=True, null=True)
    reference_no = models.TextField(blank=True, null=True)
    customer_code = models.TextField(blank=True, null=True)
    customer_id = models.IntegerField(blank=True, null=True)
    product_title_en = models.TextField(blank=True, null=True)
    product_title = models.TextField(blank=True, null=True)
    product_brand = models.TextField(blank=True, null=True)
    product_model = models.TextField(blank=True, null=True)
    product_origin = models.TextField(blank=True, null=True)
    product_material = models.TextField(blank=True, null=True)
    product_declared_name = models.TextField(blank=True, null=True)
    product_declared_name_zh = models.TextField(blank=True, null=True)
    product_sale_type = models.SmallIntegerField(blank=True, null=True)
    product_status = models.SmallIntegerField(blank=True, null=True)
    sale_status = models.SmallIntegerField(blank=True, null=True)
    receipt_status = models.SmallIntegerField(blank=True, null=True)
    product_receive_status = models.SmallIntegerField(blank=True, null=True)
    hs_code = models.TextField(blank=True, null=True)
    currency_code = models.TextField(blank=True, null=True)
    pu_code = models.TextField(blank=True, null=True)
    product_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_net_weight = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    product_weight = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    product_sales_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_purchase_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_declared_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_is_qc = models.SmallIntegerField(blank=True, null=True)
    product_barcode_type = models.SmallIntegerField(blank=True, null=True)
    product_type = models.SmallIntegerField(blank=True, null=True)
    pc_id = models.IntegerField(blank=True, null=True)
    pce_id = models.TextField(blank=True, null=True)
    product_add_time = models.DateTimeField(blank=True, null=True)
    product_update_time = models.DateTimeField(blank=True, null=True)
    product_guarantee_days = models.SmallIntegerField(blank=True, null=True)
    have_asn = models.SmallIntegerField(blank=True, null=True)
    pd_id = models.IntegerField(blank=True, null=True)
    contain_battery = models.SmallIntegerField(blank=True, null=True)
    buyer_id = models.IntegerField(blank=True, null=True)
    warning_qty = models.IntegerField(blank=True, null=True)
    warning_days = models.SmallIntegerField(blank=True, null=True)
    product_package_type = models.TextField(blank=True, null=True)
    shared_sign = models.SmallIntegerField(blank=True, null=True)
    shared_unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_describe = models.TextField(blank=True, null=True)
    product_desc_url = models.TextField(blank=True, null=True)
    shared_time = models.DateTimeField(blank=True, null=True)
    is_certificate = models.SmallIntegerField(blank=True, null=True)
    product_unit = models.TextField(blank=True, null=True)
    is_liquid = models.SmallIntegerField(blank=True, null=True)
    is_magnetic = models.SmallIntegerField(blank=True, null=True)
    pcse_id = models.IntegerField(blank=True, null=True)
    is_cainiao = models.SmallIntegerField(blank=True, null=True)
    sku_sort_code = models.TextField(blank=True, null=True)
    product_color = models.TextField(blank=True, null=True)
    product_size_type = models.TextField(blank=True, null=True)
    product_retail_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_suggested_retail_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_tax_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_style = models.TextField(blank=True, null=True)
    product_platform = models.TextField(blank=True, null=True)
    is_sync_voyage = models.SmallIntegerField(blank=True, null=True)
    use_en = models.TextField(blank=True, null=True)
    material_en = models.TextField(blank=True, null=True)
    battery_type = models.TextField(blank=True, null=True)
    receipt_receive_warehouse = models.TextField(blank=True, null=True)
    receipt_sale_warehouse = models.TextField(blank=True, null=True)
    product_origin_other = models.TextField(blank=True, null=True)
    fragile_property = models.SmallIntegerField(blank=True, null=True)
    shared_product = models.SmallIntegerField(blank=True, null=True)

    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'product'


class OmsLabelInfo(models.Model):
    order_id = models.CharField(max_length=45, blank=True, null=True)
    customer_code = models.CharField(max_length=45, blank=True, null=True)
    sku = models.CharField(max_length=100, blank=True, null=True)
    label_path = models.CharField(max_length=255, blank=True, null=True)
    is_scan = models.IntegerField(blank=True, null=True)
    who_scan = models.CharField(max_length=45, blank=True, null=True)
    wms_tracking = models.CharField(max_length=100, blank=True, null=True)
    scan_tracking = models.CharField(max_length=100, blank=True, null=True)
    label_tracking = models.CharField(max_length=100, blank=True, null=True)
    is_label_correct = models.IntegerField(blank=True, null=True)
    scan_time = models.DateTimeField(blank=True, null=True)
    add_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'oms_label_info'


class AndyCheckInTable(models.Model):
    time = models.DateTimeField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    username = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'andy_check_in_table'


class FplDirectSalePricingLog(models.Model):
    sku = models.CharField(max_length=200, blank=True, null=True, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True)
    username = models.CharField(max_length=45, blank=True, null=True)
    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'fpl_direct_sale_pricing_log'


# tracking scan program
class WebScan(models.Model):
    trailer_number = models.CharField(max_length=45, blank=True, null=True)
    username = models.CharField(max_length=45, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, null=True)
    close_date = models.DateTimeField(blank=True, null=True)
    total_box = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'web_scan'


class WebScanDetail(models.Model):
    trailer_number = models.CharField(max_length=45, blank=True, null=True)
    carrier = models.CharField(max_length=45, blank=True, null=True)
    tracking_number = models.CharField(max_length=155, blank=True, null=True)
    username = models.CharField(max_length=45, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, null=True)
    order_code = models.CharField(max_length=45, blank=True, null=True)
    product_code = models.CharField(max_length=155, blank=True, null=True)
    check_system = models.IntegerField(blank=True, null=True)
    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'web_scan_detail'


class WebScanDetailError(models.Model):
    trailer_number = models.CharField(max_length=45, blank=True, null=True)
    carrier = models.CharField(max_length=45, blank=True, null=True)
    tracking_number = models.CharField(max_length=155, blank=True, null=True)
    username = models.CharField(max_length=45, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, null=True)
    order_code = models.CharField(max_length=45, blank=True, null=True)
    product_code = models.CharField(max_length=155, blank=True, null=True)
    check_system = models.IntegerField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'web_scan_detail_error'
