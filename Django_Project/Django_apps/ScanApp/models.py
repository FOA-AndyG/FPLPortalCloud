from django.db import models


# Create your models here.
class Containerlog(models.Model):
    containerno = models.CharField(db_column='ContainerNo', max_length=50)  # Field name made lowercase.
    carrier = models.CharField(db_column='Carrier', max_length=10)  # Field name made lowercase.
    tracking = models.CharField(db_column='Tracking', max_length=50)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate')  # Field name made lowercase.
    machinename = models.CharField(db_column='MachineName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    order_code = models.CharField(db_column='order_code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    product_code = models.CharField(db_column='product_code', max_length=100, blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'ContainerLogTest'


class Containerlogerror(models.Model):
    containerno = models.CharField(db_column='ContainerNo', max_length=50)  # Field name made lowercase.
    carrier = models.CharField(db_column='Carrier', max_length=10)  # Field name made lowercase.
    tracking = models.CharField(db_column='Tracking', max_length=50)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate')  # Field name made lowercase.
    machinename = models.CharField(db_column='MachineName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    note = models.TextField(db_column='Note', blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'ContainerLogErrorTest'
