import decimal

from django.db import models
from .manager import CustomerUserManager
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from . import manager


# from phonenumber_field.modelfields import PhoneNumberField


# <-----------------------> CustomerMaster <----------------------->
class CustomerMaster(AbstractUser):
    userId = models.BigAutoField(primary_key=True)
    username = models.CharField(
        ('username'),
        max_length=30,
        unique=True,
        help_text=('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': ("A user with that username already exists."),
        },
    )
    group = models.CharField(max_length=10, blank=True, default=0)
    firstName = models.CharField('first name', max_length=30, blank=True)
    lastName = models.CharField('last name', max_length=30, blank=True)
    emailId = models.EmailField(
        verbose_name='emailId',
        max_length=40,
        blank=True,

    )
    contactNo = models.CharField(max_length=30, null=True, blank=True)
    dob = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='customer_photo', blank=True, null=True, default='')
    address = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=False)
    companyCode = models.CharField(max_length=30, blank=True, null=True)
    sw_CustomerId = models.IntegerField(null=True, blank=True)
    registration_Date = models.DateField(null=True, blank=True)
    valid_Date = models.DateField(null=True, blank=True)

    objects = CustomerUserManager()

    EMAIL_FIELD = 'emailId'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['emailId']

    class Meta:
        verbose_name = ('CustomerMaster')
        verbose_name_plural = ('CustomerMaster')

    def __str__(self):
        return self.group

    # <---------------> Member Master <-------------------->


class MemberMaster(models.Model):
    memberId = models.BigAutoField(primary_key=True)
    group = models.CharField(max_length=10, default=0)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=30)
    emailId = models.EmailField(max_length=30)
    contactNo = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        verbose_name = ('MemberMaster')
        verbose_name_plural = ('MemberMaster')

    def __str__(self):
        return self.code


# <----------------------> TranSum  <------------------------>
class TranSum(models.Model):
    TYPE = (
        ('Shares', 'Shares'),
        ('Mutual Funds', 'Mutual Funds'),
        ('Futures & Options', 'Futures & Options'),
        ('Day Trading', 'Day Trading'),
        ('Trading', 'Trading')
    )
    FY = (

        ('2021-2022', '2021-2022'),
        ('2022-2023', '2022-2023'),
        ('2023-2024', '2023-2024'),
        ('2024-2025', '2024-2025'),
        ('2025-2026', '2025-2026'),
        ('2026-2027', '2026-2027'),
        ('2027-2028', '2027-2028'),
        ('2028-2029', '2028-2029')
    )
    trId = models.BigAutoField(primary_key=True)
    group = models.CharField(max_length=10)
    code = models.CharField(max_length=10)
    fy = models.CharField(max_length=9, choices=FY)
    againstType = models.CharField(max_length=20, choices=TYPE)
    sp = models.CharField(max_length=2)
    part = models.CharField(max_length=30)
    sno = models.IntegerField(blank=True, null=True, default=0)
    fmr = models.FloatField(null=True, blank=True)
    isinCode = models.CharField(max_length=30, null=True, blank=True)
    trDate = models.DateField(null=True, blank=True)
    qty = models.IntegerField(null=True, blank=True)
    rate = models.DecimalField(max_digits=65, decimal_places=6, null=True, blank=True)
    sVal = models.DecimalField(max_digits=65, decimal_places=2, null=True, blank=True)
    sttCharges = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True)
    otherCharges = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True)
    noteAdd = models.CharField(max_length=200, blank=True)
    marketRate = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True, default=Decimal('0.00'))

    def validate_decimals(value):
        try:
            return round(float(value), 2)
        except:
            raise ValidationError(
                ('%(value)s is not an integer or a float  number'),
                params={'value': value},
            )

    marketValue = models.FloatField(validators=[validate_decimals], blank=True, null=True)
    HoldingValue = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True, default=0)
    avgRate = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True, default=0)
    scriptSno = models.IntegerField(blank=True, null=True, default=0)
    empCode = models.CharField(max_length=10, blank=True, null=True)
    clDate = models.DateField(null=True, blank=True)
    clRate = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True, default=0)
    clQTY = models.IntegerField(blank=True, null=True, default=0)
    clValue = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True, default=0)
    clsttCharges = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True, default=0)
    clOtherCharges = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True, default=0)
    balQty = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True, default=0)
    # balQty=models.IntegerField(blank=True,null=True,default=0)
    dayTrade = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True, default=0)
    strategyDate = models.DateField(null=True, blank=True)
    strategyTrigger = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True, default=0)
    entry_created_at = models.DateTimeField(auto_now_add=True, null=True)
    entry_modified_at = models.DateTimeField(auto_now=True, null=True)

    objects = models.Manager()
    purchase_objects = manager.PurchaseTranSumManager()
    master_objects = manager.MasterTranSumManager()

    def save(self, refresh_master=True, *args, **kwargs):

        master_record = TranSum.master_objects.filter(group=self.group, code=self.code, part=self.part).last()
        if self.sp is not 'M':
            # check if master record for current part exists

            if self.trId is None:

                self.balQty = self.qty
                if master_record is None:
                    # else create new master record from new purchase record and existing master records
                    master_record = TranSum.master_objects.create_master_from_purchase(self,
                                                                                       TranSum.master_objects.filter(
                                                                                           code=self.code).filter(
                                                                                           group=self.group),
                                                                                       TranSum.purchase_objects.filter(
                                                                                           part=self.part).filter(
                                                                                           group=self.group).filter(
                                                                                           code=self.code))
                    last_purchase_record = TranSum.purchase_objects.filter(group=self.group, code=self.code,
                                                                           scriptSno=self.scriptSno).last()
                    self.scriptSno = master_record.sno
                    if last_purchase_record:
                        self.sno = last_purchase_record.sno + 1
                    else:
                        self.sno = 1

            else:
                existing_record = TranSum.objects.filter(pk=self.trId).first()
                if existing_record.part is not self.part:
                    source_master_record = TranSum.master_objects.filter(group=self.group, code=self.code,
                                                                         sno=self.scriptSno).last()
                    target_master_record = TranSum.master_objects.filter(group=self.group, code=self.code,
                                                                         part=self.part).last()
                    if target_master_record is None:
                        target_master_record = TranSum.master_objects.create_master_from_purchase(self,
                                                                                                  TranSum.master_objects.filter(
                                                                                                      code=self.code).filter(
                                                                                                      group=self.group),
                                                                                                  TranSum.purchase_objects.filter(
                                                                                                      part=self.part).filter(
                                                                                                      group=self.group).filter(
                                                                                                      code=self.code))
                    master_record = target_master_record
                    self.scriptSno = master_record.sno
                    last_purchase_record = TranSum.purchase_objects.filter(group=self.group, code=self.code,
                                                                           scriptSno=self.scriptSno).last()
                    if last_purchase_record:
                        self.sno = last_purchase_record.sno + 1
                    else:
                        self.sno = 1
                    super(TranSum, self).save(*args, **kwargs)
                    source_master_record.refresh_master_record()
                self.balQty = self.balQty - (existing_record.qty - self.qty)

            self.HoldingValue = self.balQty * self.rate
            self.marketValue = self.balQty * self.marketRate
            self.avgRate = self.HoldingValue / self.balQty
            super(TranSum, self).save(*args, **kwargs)
        else:
            super(TranSum, self).save(*args, **kwargs)
        if refresh_master:
            master_record.refresh_master_record()

    def refresh_master_record(self):
        purchase_list = TranSum.purchase_objects.filter(group=self.group, code=self.code, scriptSno=self.sno)
        self.balQty = decimal.Decimal(0)
        self.HoldingValue = decimal.Decimal(0)
        for purchase in purchase_list:
            self.balQty = self.balQty + purchase.balQty
            self.HoldingValue = self.HoldingValue + purchase.HoldingValue
        self.marketValue = self.balQty * self.marketRate
        if self.balQty != 0:
            self.avgRate = self.HoldingValue / self.balQty
        self.save(refresh_master=False)
        return self

    class Meta:
        verbose_name = ('MOS_TransSum')
        verbose_name_plural = ('MOS_TransSum')


# <--------------------> MOS_Sales <--------------------->
class MOS_Sales(models.Model):
    AY = (

        ('2021-2022', '2021-2022'),
        ('2022-2023', '2022-2023'),
        ('2023-2024', '2023-2024'),
        ('2024-2025', '2024-2025'),
        ('2025-2026', '2025-2026'),
        ('2026-2027', '2026-2027'),
        ('2027-2028', '2027-2028'),
        ('2028-2029', '2028-2029')
    )
    trId = models.BigAutoField(primary_key=True)
    group = models.CharField(max_length=10)
    code = models.CharField(max_length=10)
    ay = models.CharField(max_length=9, choices=AY)
    againstType = models.CharField(max_length=15)
    scriptSno = models.IntegerField(blank=True, null=True)
    purSno = models.IntegerField(blank=True, null=True)
    sDate = models.DateField(blank=True, null=True)
    srate = models.DecimalField(max_digits=65, decimal_places=2)
    sqty = models.IntegerField()
    sVal = models.DecimalField(max_digits=65, decimal_places=2)
    stt_Paid = models.BooleanField(blank=True, null=True)
    stt = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True)
    other = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True)
    speculation = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True)
    stgc = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True)
    ltgc = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True)
    fno = models.DecimalField(max_digits=65, decimal_places=2, blank=True, null=True)
    empCode = models.CharField(max_length=10)

    class Meta:
        verbose_name = ('MOS_Sales')
        verbose_name_plural = ('MOS_Sales')
