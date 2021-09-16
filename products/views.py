from django.db.models     import Q, Count, Avg, Case, When
from django.http.response import JsonResponse

from django.views         import View
from .models              import Product, Review, UserLike
from users.models         import User
from products.decorator   import visitor_decorator


class PublicDetailView(View):
    def get(self, request, product_id):
        if not Product.objects.filter(id=product_id).exists():
            return JsonResponse({'MESSAGE':'NOT_FOUND'}, status=404)

        product      = Product.objects.prefetch_related('productimage_set')\
                        .select_related('user').get(id=product_id)
        user_product = Product.objects.filter(user=product.user.id)        
        reviews      = Review.objects.filter(product__in=user_product)

        result = {
            'user' : {
                'name'          : product.user.nickname,
                'image'         : product.user.image_url,
                'product_count' : len(user_product),
                'review_count'  : len(reviews)
            }, 
            'id'               : product.id,
            'title'            : product.title,
            'price'            : int(product.price),
            'discounted_price' : int(product.price*(100-product.discount_percent)/100),
            'discount_percent' : int(product.discount_percent),
            'description'      : product.description,
        }
        
        return JsonResponse({'result':result}, status=200)

class PrivateDetailView(View):
    @visitor_decorator
    def get(self, request, product_id):
        if not Product.objects.filter(id=product_id).exists():
            return JsonResponse({'MESSAGE':'NOT_FOUND'}, status=404)

        product      = Product.objects.annotate(\
                        is_liked=Count(Case(When(Q(userlike__user__id=request.user)\
                        &Q(userlike__product__id=product_id),then=0)),distinct=True))\
                        .prefetch_related('productimage_set').select_related('user').get(id=product_id)
        user_product = Product.objects.filter(user=product.user.id)        
        reviews      = Review.objects.filter(product__in=user_product)

        result = {
            'user' : {
                'name'          : product.user.nickname,
                'image'         : product.user.image_url,
                'product_count' : len(user_product),
                'review_count'  : len(reviews)
            }, 
            'id'               : product.id,
            'title'            : product.title,
            'price'            : int(product.price),
            'discounted_price' : int(product.price*(100-product.discount_percent)/100),
            'discount_percent' : int(product.discount_percent),
            'description'      : product.description,
            'is_liked'         : True if product.is_liked else False,
            
        }
        
        return JsonResponse({'result':result}, status=200)