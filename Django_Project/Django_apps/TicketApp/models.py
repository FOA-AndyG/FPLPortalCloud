from django.db import models


# Create your models here.
class LtlStorageRecord(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
    )

    picking_no = models.CharField(max_length=100, verbose_name="拣货单号")
    bol_no = models.CharField(max_length=100, db_index=True, verbose_name="BOL单号")
    location_code = models.CharField(max_length=50, blank=True, null=True)
    pallet_qty = models.PositiveIntegerField(verbose_name="托盘数量")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="状态")
    note = models.TextField(blank=True, null=True, verbose_name="备注")
    operator = models.CharField(max_length=50, verbose_name="操作员")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="上架时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name="提货时间")
    objects = models.Manager()

    def __str__(self):
        return f"{self.picking_no} - {self.bol_no} ({self.status})"

    class Meta:
        managed = True
        db_table = 'ltl_storage_record'


class OperationLog(models.Model):
    ACTION_CHOICES = (
        ('Created', 'Created'),
        ('Updated', 'Updated'),
        ('Shipped', 'Shipped'),
    )

    record = models.ForeignKey(LtlStorageRecord, on_delete=models.CASCADE, related_name="logs", verbose_name="关联记录")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name="操作动作")
    operator = models.CharField(max_length=50, verbose_name="操作员")
    note = models.TextField(blank=True, null=True, verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    objects = models.Manager()

    def __str__(self):
        return f"{self.record.picking_no} - {self.action} by {self.operator} at {self.created_at}"

    class Meta:
        managed = True
        db_table = 'operation_log'

