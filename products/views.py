import json
import jwt
import boto3
import requests

from unittest.main    import main
from django.views     import View
from django.conf      import settings
from django.db        import transaction
from django.http      import JsonResponse
from django.db.models import Count, Avg, Q
from django.core.exceptions import FieldError

from users.models    import User
from my_settings     import RESTAPI_KEY
from users.decorator import login_decorator
from my_settings     import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from products.models import Review, Location, MainCategory, Product, SubCategory, GatherLocation, ProductImage, UserLike


class ListCategoryView(View):
    def get(self, request, main_category_id):
        try:
            if not MainCategory.objects.filter(id=main_category_id).exists():
                return JsonResponse({'MESSAGE':'Non-Existing Main Category'}, status=404)

            sub_category_list = [
                {
                    'main_category_id'   : sub_category.main_category.id,
                    'main_category_name' : sub_category.main_category.name,
                    'sub_category_id'    : sub_category.id,
                    'sub_category_name'  : sub_category.name
                } for sub_category in SubCategory.objects.filter(main_category_id = main_category_id)
            ]
            return JsonResponse({'sub_category_list': sub_category_list}, status=200)

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

class LikeView(View):
    @login_decorator
    def post(self, request, product_id):
        if not Product.objects.filter(id=product_id):
            return JsonResponse({'MESSAGE' : 'NOT_FOUND'}, status=404)

        if UserLike.objects.filter(user=request.user,product_id=product_id).exists():
            UserLike.objects.filter(user=request.user,product_id=product_id).delete()
            return JsonResponse({'MESSAGE' : 'CANCEL_LIKE'}, status=201)
        
        UserLike.objects.create(user=request.user, product_id=product_id)
        return JsonResponse({'MESSAGE' : 'SUCCESS'}, status=201)

class ReviewView(View):    
    def get(self, request, product_id):
        if not Product.objects.filter(id=product_id).exists():
            return JsonResponse({'MESSAGE' : 'PRODUCT_NOT_FOUND'}, status=404)

        reviews = Review.objects.select_related('user').prefetch_related('reviewimage_set')\
                    .order_by('-rating').filter(product_id=product_id)
                
        result = {
            'count'        : len(reviews),
            'avg'          : round(reviews.aggregate(avg=Avg('rating'))['avg'],1) if reviews else 0,
            'perfect_rate' : len(Review.objects.filter(rating=5)) / len(reviews) * 100 if reviews else 0,
            'reviewer'     : [{
                'user'    : review.user.nickname,
                'profile' : review.user.image_url,
                'rating'  : review.rating,
                'comment' : review.comment,
                'image'   : [image.image_url for image in review.reviewimage_set.all()]
            }for review in reviews]
        }
        return JsonResponse({'result' : result}, status = 200)

class UserProductView(View):
    @login_decorator
    @transaction.atomic
    def post(self, request, user_id):
        try:
            data = json.loads(request.body)
            if not User.objects.filter(id=user_id).exists():
                return JsonResponse({"ERROR" : "USER_DOESN'T_EXIST"}, status=400)
            
            if not User.objects.get(id=user_id).bank_account_id:
                return JsonResponse({"ERROR" : "YOU'RE_NOT_A_HOST"}, status=400)
            
            if not SubCategory.objects.filter(name=data.get("sub_category")).exists():
                return JsonResponse({"ERROR" : "SUBCATEGORY_DOES'NT_EXISTS"}, status=400)

            final_price = int(float(data.get("price")) * (1 - (float(data.get("sale_percent")) / 100)))
            
            product = Product.objects.create(
                title            = data.get("title"),
                price            = final_price,
                discount_percent = float(data.get("sale_percent")),
                sub_category_id  = SubCategory.objects.get(name=data.get("sub_category")).id,
                description      = data.get("description"),
                user_id          = User.objects.get(id=user_id).id
            )

            Location.objects.create(
                product_id = product.id,
                address    = data.get("playing_location")
            )    

            GatherLocation.objects.create(
                product_id = product.id,
                address    = data.get("gather_location")
            )

            return JsonResponse({"ProductID" : product.id}, status=200)
        except Exception:
            transaction.rollback()
        except TypeError:
            return JsonResponse({"ERROR" : "TYPE_ERROR"}, status=400)
        except KeyError:
            return JsonResponse({"ERROR" : "KEY_ERROR"}, status=400)
        except ValueError:
            return JsonResponse({"ERROR" : "VALUE_ERROR"}, status=400)
    
    @login_decorator
    def get(self, request, user_id):
        if not User.objects.filter(id=user_id).exists():
            return JsonResponse({"ERROR" : "USER_DOESN'T_EXIST"}, status=404)
    
        products      = Product.objects.filter(user_id=user_id)
        products_list = [{
            "title"            : product.title,
            "price"            : product.price,
            "discount_percent" : product.discount_percent,
            "sub_category"     : product.sub_category.name,
            "description"      : product.description,
            "playing_location" : Location.objects.get(product_id=product.id).address,
            "gather_location"  : GatherLocation.objects.get(product_id=product.id).address,
            "image_url"        : [image.image_url.url for image in ProductImage.objects.filter(product_id=product.id)]
        } for product in products]

        return JsonResponse({"MESSAGE" : products_list}, status=200)

class MainPageCategoryView(View):
    def get(self, request):
        main_category_info = [
            {
                'main_category_id'        : main_category.id,
                'main_category_name'      : main_category.name,
                'main_category_image_url' : main_category.image_url
            } for main_category in MainCategory.objects.all()
        ]
        return JsonResponse({'main_category_info' : main_category_info}, status=200)

class ProductListView(View):
    def get(self, request, main_category_id):

        try:
            sub_category_id  = request.GET.get('sub_category_id', None)
            order            = request.GET.get('order', 'id')

            if not Product.objects.filter(sub_category_id__main_category_id = main_category_id).exists():
                return JsonResponse({'MESSAGE':'Non-Existing Main Category Info'}, status=404)

            q = Q()

            if main_category_id:
                q &= Q(sub_category_id__main_category_id = main_category_id)

            if sub_category_id:
                q &= Q(sub_category_id = sub_category_id)

            products = Product.objects.filter(q).annotate(rating_count = Avg('review__rating')).order_by(order)

            product_info = [
                {
                'product_id'         : product.id,
                'title'              : product.title,
                'price'              : round(float(product.price * (100 - product.discount_percent) / 100)),
                'image_url'          : [image.image_url.url for image in product.productimage_set.all()],
                'rating'             : float(round(product.rating_count, 1)) if product.rating_count else None,
                'main_category_id'   : product.sub_category.main_category.id,
                'main_category_name' : product.sub_category.main_category.name,
                'sub_category_id'    : product.sub_category_id,
                'sub_category_name'  : product.sub_category.name,
                } for product in products
            ]
            return JsonResponse({'MESSAGE' : product_info}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status=400)
        
        except FieldError:
            return JsonResponse({'MESSAGE':'FIELD_ERROR'}, status=400)

class LocationView(View):
    def get(self, request, product_id):
        try:
            if not Product.objects.filter(id=product_id).exists():
                return JsonResponse({'MESSAGE' : 'PRODUCT_NOT_FOUND'}, status=404)
            
            location        = Location.objects.get(product_id=product_id)
            gather          = GatherLocation.objects.get(product_id=product_id)
            headers         = {'Authorization': f'KakaoAK {RESTAPI_KEY}'}
            location_querys = {'query' : location.address, 'analyze_type' : 'exact'}
            gather_querys   = {'query' : gather.address, 'analyze_type' : 'exact'}

            location_request = requests.post('https://dapi.kakao.com/v2/local/search/address.json', \
                                params=location_querys, headers=headers, timeout=3)
            gather_request   = requests.post('https://dapi.kakao.com/v2/local/search/address.json', \
                                params=gather_querys, headers=headers, timeout=3)
            
            location_longitude = float(location_request.json().get('documents')[0].get('x'))
            location_latitude  = float(location_request.json().get('documents')[0].get('y'))
            gather_longitude   = float(gather_request.json().get('documents')[0].get('x'))
            gather_latitude    = float(gather_request.json().get('documents')[0].get('y'))


            result = {
                'location' : {
                    'x' : round(location_longitude, 5),
                    'y' : round(location_latitude, 5)
                },
                'gather' : {
                    'x' : round(gather_longitude, 5),
                    'y' : round(gather_latitude, 5)
                }
            }
            return JsonResponse({'result' : result}, status=200)
            
        except Location.DoesNotExist:
            return JsonResponse({'MESSAGE' : 'LOCATION_NOT_FOUND'}, status=404)

        except GatherLocation.DoesNotExist:
            return JsonResponse({'MESSAGE' : 'GATHER_NOT_FOUND'}, status=404)

        except requests.exceptions.ConnectTimeout:
            return JsonResponse({'MESSAGE' : 'TIME_OUT'}, status=408)

        except IndexError:
            return JsonResponse({'MESSAGE' : 'WRONG_ADDRESS'}, status=401)            
        return JsonResponse({'main_category_info' : main_category_info}, status=200)

class ImageUploadView(View):
    s3_client = boto3.client(
        's3',
        aws_access_key_id     = AWS_ACCESS_KEY_ID,
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
    )
    @login_decorator
    @transaction.atomic
    def post(self, request, user_id, product_id):
        try:
            if not User.objects.filter(id=user_id).exists():
                return JsonResponse({"ERROR" : "USER_DOESN'T_EXIST"}, status=400)
            
            if not User.objects.get(id=user_id).bank_account_id:
                return JsonResponse({"ERROR" : "YOU'RE_NOT_A_HOST"}, status=400)
            
            product = Product.objects.get(id=product_id)

            image_list = request.FILES.getlist("image_url")
            [self.s3_client.upload_fileobj(
                image,
                "flip-test2",
                image.name,
                ExtraArgs={
                    "ContentType" : image.content_type
                }
            )for image in image_list]

            [ProductImage.objects.create(
                product_id = product.id,
                image_url  = image.name
            ) for image in image_list]

            return JsonResponse({"MESSAGE" : "CREATE"}, status=200)
        except Exception:
            transaction.rollback()
        except TypeError:
            return JsonResponse({"ERROR" : "TYPE_ERROR"}, status=400)
        except KeyError:
            return JsonResponse({"ERROR" : "KEY_ERROR"}, status=400)
        except ValueError:
            return JsonResponse({"ERROR" : "VALUE_ERROR"}, status=400)