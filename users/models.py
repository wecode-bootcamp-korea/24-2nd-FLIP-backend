from core.models import SoftDeleteModel, TimeStampModel
from django.db   import models

class User(TimeStampModel, SoftDeleteModel):
    kakao_id        = models.IntegerField(unique=True)
    email           = models.EmailField(max_length=250, null=True, unique=True)
    password        = models.CharField(max_length=2000, null=True)
    nickname        = models.CharField(max_length=100)
    image_url       = models.URLField(null=True)
    bank_account_id = models.ForeignKey('BankAccount', null=True, on_delete=models.SET_NULL)
    soft_delete     = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'

class BankAccount(TimeStampModel):
    account_number = models.IntegerField()
    bank_id        = models.ForeignKey('Bank', on_delete=models.PROTECT)
    account_holder = models.CharField(max_length=100)

    class Meta:
        db_table = 'bank_accounts'

class Bank(TimeStampModel):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'banks'


