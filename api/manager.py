from django.contrib.auth.base_user import BaseUserManager
from django.db import models


class CustomerUserManager(BaseUserManager):
    def create_user(self, username, emailId, password=None, password2=None, **extra_fields):

        if not username:
            raise ValueError('The given username must be set')
        emailId = self.normalize_email(emailId)
        user = self.model(username=username, emailId=emailId, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, emailId, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, emailId, password, **extra_fields)


class MasterTranSumManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(sp='M')

    def create_master_from_purchase(self, purchase_record):
        master_record = self.model(code=purchase_record.code, group=purchase_record.group, fy=purchase_record.fy,
                                   fmr=purchase_record.fmr, isinCode=purchase_record.isinCode,
                                   againstType=purchase_record.againstType, part=purchase_record.part,
                                   sp='M')

        master_record.save()
        return master_record


class PurchaseTranSumManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().exclude(sp='M')
