from core.models  import TimeStampModel
from django.db    import models

from users.models import User

class Product(TimeStampModel):
    title            = models.CharField(max_length=50)
    price            = models.DecimalField(max_digits=13, decimal_places=3)
    discount_percent = models.DecimalField(max_digits=6, decimal_places=3)
    sub_category     = models.ForeignKey('SubCategory', null=True, on_delete=models.SET_NULL)
    description      = models.TextField()
    user             = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'products'

class SubCategory(TimeStampModel):
    name          = models.CharField(max_length=50)
    main_category = models.ForeignKey('MainCategory', null=True, on_delete=models.SET_NULL) 

    class Meta:
        db_table = 'sub_categories'

class MainCategory(TimeStampModel):
    name      = models.CharField(max_length=50)
    image_url = models.URLField(null=True)

    class Meta:
        db_table = 'main_categories'

class Location(TimeStampModel):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    address = models.CharField(max_length=50)

    class Meta:
        db_table = 'locations'

class GatherLocation(TimeStampModel):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    address = models.CharField(max_length=50)

    class Meta:
        db_table = 'gather_locations'

class ProductImage(TimeStampModel):
    image_url = models.ImageField()
    product   = models.ForeignKey('Product', on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_images'

class Review(TimeStampModel):
    rating  = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    comment = models.TextField(null=True)
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    class Meta:
        db_table = 'reviews'

class ReviewImage(TimeStampModel):
    image_url = models.ImageField()
    review    = models.ForeignKey('Review', on_delete=models.CASCADE) 

    class Meta:
        db_table = 'review_images'

class UserLike(TimeStampModel):
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'user_likes'