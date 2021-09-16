import json
import jwt

from django.test      import TestCase, Client
from django.views     import View
from django.http      import HttpResponse, JsonResponse
from django.db.models import Q, Count, Avg, Case, When
from django.conf      import settings

from .models          import Product, Review, ProductImage
from users.models     import User

class PublicDetailTest(TestCase):
    @classmethod					
    def setUpTestData(cls):				
        user = User.objects.create(
            id        = 1,
            kakao_id  = 1,
            nickname  = "dongpalli",
            image_url = "https://www.frip.co.kr/products/125411"
        )
        product = Product.objects.create(
            id               = 1,
            title            = "필라테스 강습",
            price            = 200000,
            discount_percent = 10,
            description      = "그냥 사",
            user             = user
        )
        reviews = Review.objects.create(
            rating  = 5.0,
            comment = "좋아 죽어요",
            user    = user,
            product = product
        )
        product_image = ProductImage.objects.create(
            image_url = "hello",
            product   = product
        )
            
    def test_public_detail_get_not_found_fail(self):
        client   = Client()
        # when
        response = client.get('/public/product/0')
        # then 
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'MESSAGE':'NOT_FOUND'})

    def test_public_detail_get_success(self):
        client   = Client()
        # when 
        response = client.get('/public/product/1')
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                "result": {
                    "user": {
                        "name"          : "dongpalli",
                        "image"         : "https://www.frip.co.kr/products/125411",
                        "product_count" : 1,
                        "review_count"  : 1
                    },
                    "id"               : 1,
                    "title"            : "필라테스 강습",
                    "price"            : 200000,
                    "discounted_price" : 180000,
                    "discount_percent" : 10,
                    "description"      : "그냥 사",
                }   
            }
        )

class PrivateDetailTest(TestCase):
    @classmethod					
    def setUpTestData(cls):				
        user = User.objects.create(
            id        = 2,
            kakao_id  = 2,
            nickname  = "dongpalli",
            image_url = "www.dk.com"
        )
        product = Product.objects.create(
            id               = 2,
            title            = "필라테스 강습",
            price            = 0,
            discount_percent = 10,
            description      = "그냥 사",
            user             = user
        )
        reviews = Review.objects.create(
            rating  = 5.0,
            comment = "좋아 죽어요",
            user    = user,
            product = product
        )
        product_image = ProductImage.objects.create(
            image_url = "hello",
            product   = product
        )
    
    def test_private_detail_get_not_found_fail(self):
        access_token = jwt.encode({'id' : 2}, settings.SECRET_KEY,algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}
        client       = Client()
        # when
        response = client.get('/private/product/0', **headers)
        # then 
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'MESSAGE':'NOT_FOUND'})

    def test_private_detail_get_wrong_access_fail(self):
        headers = {"HTTP_Authorization": "fake_token"}
        client  = Client()
        # when
        response = client.get('/private/product/0', **headers)
        # then 
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'MESSAGE':'WRONG_ACCESS'})

    def test_private_detail_get_invalid_user_fail(self):
        access_token = jwt.encode({'id' : 5}, settings.SECRET_KEY,algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}
        client       = Client()
        # when
        response = client.get('/private/product/0', **headers)
        # then 
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'MESSAGE':'INVALID_USER'})

    def test_public_detail_get_success(self):
        access_token = jwt.encode({'id' : 2}, settings.SECRET_KEY,algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}
        client       = Client()
        # when 
        response = client.get('/private/product/2', **headers)
        #then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                "result": {
                    "user": {
                        "name"          : "dongpalli",
                        "image"         : "www.dk.com",
                        "product_count" : 1,
                        "review_count"  : 1
                    },
                    "id"               : 2,
                    "title"            : "필라테스 강습",
                    "price"            : 0,
                    "discounted_price" : 0,
                    "discount_percent" : 10,
                    "description"      : "그냥 사",
                    "is_liked"         : False
                }   
            }
        )