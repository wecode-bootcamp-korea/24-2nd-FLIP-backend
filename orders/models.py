from django.db                 import models
from django.db.models.deletion import SET_NULL

from users.models    import User
from products.models import Product
from core.models     import TimeStampModel

class Order(TimeStampModel):
    order_status = models.ForeignKey('OrderStatus', null=True, on_delete=models.SET_NULL)
    final_price  = models.DecimalField(max_digits=13, decimal_places=3)
    user         = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'orders'

class OrderStatus(TimeStampModel):
    status = models.CharField(max_length=50)

    class Meta:
        db_table = 'order_status'

class OrderItem(TimeStampModel):
    order    = models.ForeignKey('Order', on_delete=models.CASCADE)
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField

    class Meta:
        db_table = 'order_items'
    
class Payment(TimeStampModel):
    order        = models.ForeignKey('Order', on_delete=models.CASCADE)
    method       = models.ForeignKey('Method', null=True, on_delete=SET_NULL)
    final_amount = models.DecimalField(max_digits=13, decimal_places=3, null=True)
    status       = models.CharField(max_length=50, default='ready')

    class Meta:
        db_table = 'payments'

class Method(TimeStampModel):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'methods'
