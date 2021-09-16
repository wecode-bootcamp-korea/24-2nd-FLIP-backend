
import jwt
import json
from unittest.main import main
from .models       import Product, Review, UserLike
from users.models  import User

from django.conf     import settings
from django.http     import JsonResponse
from django.views    import View
from django.db.models import Count

from products.models import MainCategory, SubCategory

class ListCategoryView(View):
    def get(self, request, main_category_id):
        try:
            if not MainCategory.objects.filter(id=main_category_id).exists():
                return JsonResponse({'MESSAGE':'Non-Existing Main Category'}, status=404)

            sub_category_list = [
                {
                    'sub_category_id' : sub_category.id,
                    'sub_category_name' : sub_category.name
                } for sub_category in SubCategory.objects.filter(main_category_id = main_category_id)
            ]
            return JsonResponse({'sub_category_list':sub_category_list}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status=400)

        except ValueError:
            return JsonResponse({'MESSAGE':'VALUE_ERROR'}, status=400)

class ProductDetailView(View): 
    def check_like(self, request, product_id):
        try:           
            access_token = request.headers.get('Authorization', None)
            if not access_token:
                return False
            token = jwt.decode(access_token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(kakao_id=token['id'])
            if not UserLike.objects.filter(user=user,product_id=product_id).exists():
                return False
        except jwt.exceptions.DecodeError:
            raise Exception
        except User.DoesNotExist:
            return False
        return True
    
    def get(self, request, product_id):
        try:       
            if not Product.objects.filter(id=product_id).exists():
                return JsonResponse({'MESSAGE':'NOT_FOUND'}, status=404)
            
            product      = Product.objects.prefetch_related('productimage_set').select_related('user')\
                            .annotate(like_count=Count("userlike",distinct=True)).get(id=product_id)
            user_product = Product.objects.filter(user=product.user.id)        
            reviews      = Review.objects.filter(product__in=user_product)

            result = {
                'user' : {
                    'id'            : product.user.id,
                    'name'          : product.user.nickname,
                    'image'         : product.user.image_url,
                    'product_count' : len(user_product),
                    'review_count'  : len(reviews)
                }, 
                'id'               : product.id,
                'title'            : product.title,
                'price'            : int(product.price),
                'image'            : [image.image_url.url for image in product.productimage_set.all()],
                'discounted_price' : int(product.price*(100-product.discount_percent)/100),
                'discount_percent' : int(product.discount_percent),
                'description'      : product.description,
                'like_count'       : product.like_count,
                'is_liked'         : self.check_like(request, product_id),
                
            }
            return JsonResponse({'result':result}, status=200)

        except Exception:
            return JsonResponse({"MESSAGE" : "WRONG_ACCESS"}, status=401)   
