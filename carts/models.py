from core.models     import TimeStampModel
from django.db       import models

from products.models import Product
from users.models    import User

class Cart(TimeStampModel):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE)
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity   = models.IntegerField()

    class Meta:
        db_table = 'carts'

