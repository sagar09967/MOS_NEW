import decimal

from django.db import models
from .manager import CustomerUserManager
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from . import manager
from dateutil.relativedelta import relativedelta
from . import services


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
    part = models.CharField(max_length=100)
    sno = models.IntegerField(blank=True, null=True, default=0)
    fmr = models.FloatField(null=True, blank=True)
    isinCode = models.CharField(max_length=30, null=True, blank=True)
    trDate = models.DateField(null=True, blank=True)
    qty = models.IntegerField(null=True, blank=True)
    rate = models.DecimalField(max_digits=65, decimal_places=17, null=True, blank=True)
    sVal = models.DecimalField(max_digits=65, decimal_places=17, null=True, blank=True)
    sttCharges = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True)
    otherCharges = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True)
    noteAdd = models.CharField(max_length=200, blank=True)
    marketRate = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True, default=Decimal('0.00'))

    def validate_decimals(value):
        try:
            return round(float(value), 2)
        except:
            raise ValidationError(
                ('%(value)s is not an integer or a float  number'),
                params={'value': value},
            )

    marketValue = models.FloatField(validators=[validate_decimals], blank=True, null=True)
    HoldingValue = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True, default=0)
    avgRate = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True, default=0)
    scriptSno = models.IntegerField(blank=True, null=True, default=0)
    empCode = models.CharField(max_length=10, blank=True, null=True)
    clDate = models.DateField(null=True, blank=True)
    clRate = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True, default=0)
    clQTY = models.IntegerField(blank=True, null=True, default=0)
    clValue = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True, default=0)
    clsttCharges = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True, default=0)
    clOtherCharges = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True, default=0)
    balQty = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True, default=0)
    # balQty=models.IntegerField(blank=True,null=True,default=0)
    dayTrade = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True, default=0)
    strategyDate = models.DateField(null=True, blank=True)
    strategyTrigger = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True, default=0)
    # entry_created_at = models.DateTimeField(auto_now_add=True, null=True)
    # entry_modified_at = models.DateTimeField(auto_now=True, null=True)

    objects = models.Manager()
    purchase_objects = manager.PurchaseTranSumManager()
    master_objects = manager.MasterTranSumManager()

    def save(self, *args, **kwargs):
        super(TranSum, self).save(*args, **kwargs)
        if self.sp == 'A' or self.sp == 'O':
            master_record = TranSum.master_objects.filter(group=self.group, code=self.code, part=self.part,
                                                          againstType=self.againstType).last()
            if master_record is None:
                master_record = TranSum.master_objects.create_master_from_purchase(self)
            queryset = TranSum.purchase_objects.filter(pk=self.trId)  # this record itself
            scriptSno = master_record.sno
            sno = self.sno
            if self.sno is 0:
                last_purchase_for_part = TranSum.purchase_objects.filter(group=self.group, code=self.code,
                                                                         scriptSno=master_record.sno,
                                                                         part=self.part,
                                                                         againstType=self.againstType).last()
                if last_purchase_for_part:
                    sno = last_purchase_for_part.sno + 1
                else:
                    sno = 1

            sales_for_current_purchase = MOS_Sales.objects.filter(group=self.group, code=self.code, purSno=self.sno,
                                                                  scriptSno=self.scriptSno,
                                                                  againstType=self.againstType)
            balQty = self.qty - sum_by_key(sales_for_current_purchase, 'sqty')
            market_rate = services.get_market_rate(self.part)
            if market_rate:
                market_rate = market_rate['Adj Close']
                marketValue = balQty * market_rate
            else:
                market_rate = None
                marketValue = None
            HoldingValue = balQty * self.rate
            if balQty > 0:
                avgRate = HoldingValue / balQty
            else:
                avgRate = 0
            values = {'scriptSno': scriptSno, 'sno': sno, 'balQty': balQty, 'marketValue': marketValue,
                      'HoldingValue': HoldingValue, 'avgRate': avgRate, 'marketRate': market_rate}
            update = queryset.update(**values)  # update this record with derived values
            master_record.save()
            for sale in sales_for_current_purchase:
                sale.refresh_stcg_ltcg(queryset.first(), *args, **kwargs)
            return self

        if self.sp == 'M':
            scriptSno = 0
            sno = self.sno
            if self.sno is 0:
                last_master_for_user = TranSum.master_objects.filter(group=self.group, code=self.code,
                                                                     againstType=self.againstType).exclude(
                    pk=self.trId).last()
                if last_master_for_user:
                    sno = last_master_for_user.sno + 1
                else:
                    sno = 1
            purchases_by_part = TranSum.purchase_objects.filter(group=self.group, code=self.code, part=self.part,
                                                                againstType=self.againstType)
            purchases_by_part.update(scriptSno=sno)
            balQty = sum_by_key(purchases_by_part, 'balQty')
            HoldingValue = sum_by_key(purchases_by_part, 'HoldingValue')
            market_rate = services.get_market_rate(self.part)
            if market_rate:
                market_rate = Decimal(market_rate['Adj Close'])
            else:
                market_rate = 0
            marketValue = balQty * market_rate
            avgRate = 0
            if balQty != 0:
                avgRate = HoldingValue / balQty
            values = {'scriptSno': scriptSno, 'sno': sno, 'balQty': balQty, 'marketValue': marketValue,
                      'HoldingValue': HoldingValue, 'avgRate': avgRate, 'marketRate': market_rate}
            queryset = TranSum.master_objects.filter(pk=self.trId)
            queryset.update(**values)
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
    fy = models.CharField(max_length=9, choices=AY)
    againstType = models.CharField(max_length=15)
    scriptSno = models.IntegerField(blank=True, null=True)
    purSno = models.IntegerField(blank=True, null=True)
    sDate = models.DateField(blank=True, null=True)
    srate = models.DecimalField(max_digits=65, decimal_places=17)
    sqty = models.IntegerField()
    sVal = models.DecimalField(max_digits=65, decimal_places=17)
    stt_Paid = models.BooleanField(blank=True, null=True)
    stt = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True)
    other = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True)
    speculation = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True)
    stcg = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True)
    ltcg = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True)
    fno = models.DecimalField(max_digits=65, decimal_places=17, blank=True, null=True)
    empCode = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        purchase_record = TranSum.purchase_objects.filter(sno=self.purSno, scriptSno=self.scriptSno, group=self.group,
                                                          code=self.code, againstType=self.againstType).first()
        existing_qty = 0
        if self.trId:
            existing_sale_record = MOS_Sales.objects.filter(pk=self.trId).first()
            existing_qty = existing_sale_record.sqty

        if purchase_record.balQty + existing_qty - self.sqty < 0:
            raise ValidationError(
                "Balance Quantity on purchase record is not sufficient to record this sale against it.")
        master_record = TranSum.master_objects.filter(group=self.group, code=self.code,
                                                      sno=purchase_record.scriptSno,
                                                      againstType=self.againstType).first()
        purchase_record.clDate = self.sDate
        purchase_record.clRate = self.srate
        purchase_record.clQTY = self.sqty
        purchase_record.clValue = self.sVal
        purchase_record.clsttCharges = self.stt
        purchase_record.clOtherCharges = self.other
        self.scriptSno = master_record.sno
        super(MOS_Sales, self).save(*args, **kwargs)
        self.refresh_stcg_ltcg(purchase_record, *args, **kwargs)
        purchase_record.save()  # refreshes master

    def refresh_stcg_ltcg(self, purchase_record, *args, **kwargs):
        time_delta = relativedelta(self.sDate, purchase_record.trDate)
        if self.againstType == 'Day Trading':
            self.stcg = 0
            self.ltcg = 0
        elif (time_delta.years * 12 + time_delta.months) <= 12:
            self.stcg = self.sVal - (self.sqty * purchase_record.rate)
            self.ltcg = 0
        else:
            self.stcg = 0
            self.ltcg = self.sVal - (self.sqty * purchase_record.rate)
        super(MOS_Sales, self).save()

    class Meta:
        verbose_name = ('MOS_Sales')
        verbose_name_plural = ('MOS_Sales')


class Feedback(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.CharField(max_length=10)
    note = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)


class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    caption = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    image = models.ImageField(blank=True, null=True, upload_to='Post_Images/post/')
    post_url = models.URLField(blank=True, null=True)


class ReleaseNote(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    note = models.TextField(blank=False, null=False)
    date = models.DateField(null=True, blank=True)


def sum_by_key(records, key):
    sum_result = 0
    for record in records:
        sum_result = sum_result + getattr(record, key)
    return sum_result
