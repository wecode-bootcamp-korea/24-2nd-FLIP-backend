import jwt
from products.models  import MainCategory, SubCategory, Product, UserLike
from django.test      import TestCase, Client
from django.conf      import settings

from .models          import Product, Review, ProductImage, UserLike
from users.models     import User

class MainCategoryTest(TestCase):
    def setUp(self):
        main_category = MainCategory.objects.create(
            id        = 1,
            name      = "아웃도어",
            image_url = "https://images.ctfassets.net/hrltx12pl8hq/38KzANR5RR0lZ8jPlkOMwr/91b5342346b92bdf11c35a862e747d03/01-parks-outdoors_1661119069.jpg?fit=fill&w=480&h=270"
        )

        SubCategory.objects.create(
            id            = 1,
            name          = "서핑",
            main_category = main_category,
        )

    def tearDown(self):
        MainCategory.objects.all().delete()
        SubCategory.objects.all().delete()

    def test_listcategory_get_success(self):
        client   = Client()
        response = client.get("/products/main_category/1")
        self.assertEqual(response.json(),
            {
                "sub_category_list" : [
                    {
                        "sub_category_id" : 1,
                        "sub_category_name" : "서핑"
                    }
                ]
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_listcategory_get_error(self):
            client   = Client()
            response = client.get('/products/main_category/20000')
            self.assertEqual(response.json(),
                {
                    'MESSAGE' : 'Non-Existing Main Category'
                }
            )
            self.assertEqual(response.status_code, 404)

class ProductDetailTest(TestCase):
    @classmethod					
    def setUpTestData(cls):				
        user = User.objects.create(
            id        = 3,
            kakao_id  = 3,
            nickname  = "dongpalli",
            image_url = "www.dk.com"
        )
        user2 = User.objects.create(
            id        = 4,
            kakao_id  = 4,
            nickname  = "dongpalli",
            image_url = "www.dk.com"
        )
        product = Product.objects.create(
            id               = 3,
            title            = "필라테스 강습",
            price            = 100,
            discount_percent = 10,
            description      = "그냥 사",
            user             = user
        )
        product2 = Product.objects.create(
            id               = 4,
            title            = "촬영 강습",
            price            = 100,
            discount_percent = 10,
            description      = "그냥 사세요",
            user             = user2
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
        like = UserLike.objects.create(
            id      = 1,
            user    = user,
            product = product
        )
    def test_product_detail_get_token_not_found_fail(self):
        client       = Client()        
        access_token = jwt.encode({'id' : 3}, settings.SECRET_KEY,algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}        
        response     = client.get('/product/0', **headers)        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'MESSAGE':'NOT_FOUND'})

    def test_product_detail_get_none_token_not_found_fail(self):
        client       = Client()        
        response     = client.get('/product/0')        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'MESSAGE':'NOT_FOUND'})

    def test_product_detail_get_token_like_true_success(self):
        client       = Client()        
        access_token = jwt.encode({'id' : 3}, settings.SECRET_KEY,algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}        
        response = client.get('/product/3', **headers) 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                "result": {
                    "user": {
                        "id"            : 3,
                        "name"          : "dongpalli",
                        "image"         : "www.dk.com",
                        "product_count" : 1,
                        "review_count"  : 1
                    },
                    "id"               : 3,
                    "title"            : "필라테스 강습",
                    "price"            : 100,
                    "image"            : ['https://flip-back.s3.ap-northeast-2.amazonaws.com/media/hello'],
                    "discounted_price" : 90,
                    "discount_percent" : 10,
                    "description"      : "그냥 사",
                    'like_count'       : 1,
                    "is_liked"         : True
                }   
            }
        )
    def test_product_detail_get_token_like_false_success(self):
        client       = Client()        
        access_token = jwt.encode({'id' : 3}, settings.SECRET_KEY,algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}        
        response = client.get('/product/4', **headers)        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                "result": {
                    "user": {
                        "id"            : 4,
                        "name"          : "dongpalli",
                        "image"         : "www.dk.com",
                        "product_count" : 1,
                        "review_count"  : 0
                    },
                    "id"               : 4,
                    "title"            : "촬영 강습",
                    "price"            : 100,
                    "image"            : [],
                    "discounted_price" : 90,
                    "discount_percent" : 10,
                    "description"      : "그냥 사세요",
                    'like_count'       : 0,
                    "is_liked"         : False
                }   
            }
        )

    def test_product_detail_get_none_token_success(self):
        client       = Client()
        response     = client.get('/product/3')        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                "result": {
                    "user": {
                        "id"            : 3,
                        "name"          : "dongpalli",
                        "image"         : "www.dk.com",
                        "product_count" : 1,
                        "review_count"  : 1
                    },
                    "id"               : 3,
                    "title"            : "필라테스 강습",
                    "price"            : 100,
                    "image"            : ['https://flip-back.s3.ap-northeast-2.amazonaws.com/media/hello'],
                    "discounted_price" : 90,
                    "discount_percent" : 10,
                    "description"      : "그냥 사",
                    'like_count'       : 1,
                    "is_liked"         : False
                }   
            }
        )

    def test_product_detail_get_token_user_not_exist_success(self):
        client       = Client()
        access_token = jwt.encode({'id' : 5}, settings.SECRET_KEY,algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}
        response = client.get('/product/3', **headers)        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                "result": {
                    "user": {
                        "id"            : 3,
                        "name"          : "dongpalli",
                        "image"         : "www.dk.com",
                        "product_count" : 1,
                        "review_count"  : 1
                    },
                    "id"               : 3,
                    "title"            : "필라테스 강습",
                    "price"            : 100,
                    "image"            : ['https://flip-back.s3.ap-northeast-2.amazonaws.com/media/hello'],
                    "discounted_price" : 90,
                    "discount_percent" : 10,
                    "description"      : "그냥 사",
                    'like_count'       : 1,
                    "is_liked"         : False
                }   
            }
        )

    def test_product_detail_get_token_decode_error_fail(self):
        client       = Client()        
        headers      = {"HTTP_Authorization": "fake_token"}        
        response     = client.get('/product/3', **headers)        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'MESSAGE':'WRONG_ACCESS'})

class LikeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.bulk_create([            
            User(id=1, kakao_id=1, nickname="palli"),
            User(id=2, kakao_id=2, nickname="dong")
            ])
        product = Product.objects.create(
            id               = 1,
            title            = "필라테스 강습",
            price            = 100,
            discount_percent = 10,
            description      = "그냥 사",
            user_id          = 1
        )
        like = UserLike.objects.create(
            id      = 2,
            user_id = 2,
            product = product
        )
    
    def test_like_post_not_found_fail(self):
        client = Client()
        access_token = jwt.encode({'id' : 1}, settings.SECRET_KEY,algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}
        response     = client.post('/product/0/like', **headers)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json(), {'MESSAGE' : 'NOT_FOUND'})

    def test_like_post_success(self):
        client       = Client()
        access_token = jwt.encode({'id' : 1}, settings.SECRET_KEY,algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}
        response     = client.post('/product/1/like', **headers)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json(), {'MESSAGE' : 'SUCCESS'})

    def test_like_cancel_post_success(self):
        client       = Client()        
        access_token = jwt.encode({'id' : 2}, settings.SECRET_KEY,algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}
        response     = client.post('/product/1/like', **headers)        
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json(), {'MESSAGE' : 'CANCEL_LIKE'})

    def test_like_does_not_exist_error_fail(self):
        client       = Client()        
        access_token = jwt.encode({'id' : 99}, settings.SECRET_KEY,algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}        
        response     = client.post('/product/1/like', **headers)        
        self.assertEqual(response.status_code,401)
        self.assertEqual(response.json(), {'MESSAGE' : 'INVALID_USER'})

    def test_like_decode_error_fail(self):
        client       = Client()        
        headers      = {"HTTP_Authorization": "fake_token"}        
        response     = client.post('/product/1/like', **headers)        
        self.assertEqual(response.status_code,401)
        self.assertEqual(response.json(), {'MESSAGE' : 'ENCODE_ERROR'}) 