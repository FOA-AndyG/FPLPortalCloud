from django.db import models


# Create your models here.
class Login(models.Model):
    username = models.CharField(max_length=25)
    password = models.CharField(max_length=25)
    fullname = models.CharField(db_column='FullName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    firstname = models.CharField(max_length=100, blank=True, null=True)
    lastname = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(db_column='Email', max_length=100, blank=True, null=True)  # Field name made lowercase.
    updates = models.IntegerField(db_column='Updates', blank=True, null=True)  # Field name made lowercase.
    department = models.CharField(max_length=50, blank=True, null=True)
    newuser = models.IntegerField(blank=True, null=True)
    ip = models.CharField(db_column='IP', max_length=50, blank=True, null=True)
    lunch = models.IntegerField(blank=True, null=True)
    ext = models.CharField(max_length=3, blank=True, null=True)
    emailpassword = models.CharField(db_column='EmailPassword', max_length=10, blank=True, null=True)  # Field name made lowercase.
    windowslogin = models.CharField(db_column='WindowsLogin', max_length=30, blank=True, null=True)  # Field name made lowercase.
    profitshare = models.IntegerField(db_column='profitShare', blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(max_length=45, blank=True, null=True)

    objects = models.manager

    class Meta:
        managed = False
        db_table = 'login'


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_code = models.CharField(unique=True, max_length=32)
    reference_no = models.CharField(max_length=64)
    customer_id = models.IntegerField()
    customer_code = models.CharField(max_length=8)
    platform = models.CharField(max_length=20)
    order_type = models.IntegerField()
    create_type = models.CharField(max_length=20)
    order_platform_type = models.CharField(max_length=20)
    order_business_type = models.CharField(max_length=12, blank=True, null=True)
    warehouse_id = models.IntegerField()
    to_warehouse_id = models.IntegerField()
    is_oda = models.IntegerField()
    oda_type = models.IntegerField()
    is_signature = models.IntegerField()
    is_insurance = models.IntegerField()
    insurance_value = models.DecimalField(max_digits=10, decimal_places=3)
    country_code = models.CharField(max_length=4)
    mp_code = models.CharField(max_length=64)
    sm_code = models.CharField(max_length=32)
    sc_id = models.IntegerField()
    order_advance_pickup = models.IntegerField()
    parcel_declared_value = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee_estimate = models.DecimalField(max_digits=10, decimal_places=3)
    currency_code = models.CharField(max_length=5)
    parcel_contents = models.CharField(max_length=255)
    parcel_quantity = models.IntegerField()
    order_status = models.IntegerField()
    order_sub_status = models.IntegerField()
    problem_status = models.IntegerField()
    underreview_status = models.IntegerField()
    upload_express_status = models.IntegerField()
    anew_express_status = models.IntegerField()
    intercept_status = models.IntegerField()
    order_waiting_status = models.IntegerField()
    order_picking_status = models.IntegerField()
    order_charge_status = models.IntegerField()
    sync_status = models.IntegerField()
    sync_cost_status = models.IntegerField(blank=True, null=True)
    print_sort = models.IntegerField()
    print_quantity = models.IntegerField()
    add_time = models.DateTimeField()
    update_time = models.DateTimeField()
    order_paydate = models.DateTimeField(blank=True, null=True)
    order_pick_type = models.IntegerField()
    picking_basket = models.CharField(max_length=20)
    picker_id = models.IntegerField()
    remark = models.CharField(max_length=255)
    site_id = models.CharField(max_length=64)
    seller_id = models.CharField(max_length=128)
    buyer_id = models.CharField(max_length=64)
    buyer_name = models.CharField(max_length=64)
    buyer_mail = models.CharField(max_length=128)
    operator_note = models.CharField(max_length=255, blank=True, null=True)
    order_exception_status = models.IntegerField()
    order_exception_type = models.PositiveIntegerField()
    order_exception_sub_type = models.IntegerField()
    shared_sign = models.IntegerField(blank=True, null=True)
    is_returns = models.IntegerField()
    is_residential = models.IntegerField(blank=True, null=True)
    check_shipping_method = models.IntegerField()
    validate_address_sign = models.IntegerField()
    platform_shop = models.CharField(max_length=128)
    order_charge_type = models.IntegerField()
    sync_service_status = models.IntegerField()
    sync_count = models.IntegerField()
    sync_wms_sign = models.IntegerField()
    sync_required_sign = models.IntegerField(blank=True, null=True)
    sync_wms_status = models.IntegerField()
    sync_wms_time = models.DateTimeField(blank=True, null=True)
    sync_customs_status = models.IntegerField()
    sync_customs_sub_status = models.IntegerField()
    sync_customs_time = models.DateTimeField(blank=True, null=True)
    sync_customs_msg = models.CharField(max_length=255, blank=True, null=True)
    add_user = models.CharField(max_length=64)
    lp_code = models.CharField(max_length=32)
    is_sync_erp = models.IntegerField()
    org_refrence_no_platform = models.CharField(max_length=64)
    is_cut_off = models.IntegerField()
    carrier_name = models.CharField(max_length=100)

    objects = models.manager

    class Meta:
        managed = False
        db_table = 'orders'


class ContainerLog(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    containerno = models.CharField(db_column='ContainerNo', max_length=50)  # Field name made lowercase.
    carrier = models.CharField(db_column='Carrier', max_length=10)  # Field name made lowercase.
    tracking = models.CharField(db_column='Tracking', max_length=50)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate')  # Field name made lowercase.
    machinename = models.CharField(db_column='MachineName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    order_code = models.CharField(max_length=50, blank=True, null=True)
    product_code = models.CharField(max_length=100, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'ContainerLog'
