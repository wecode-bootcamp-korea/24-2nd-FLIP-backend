import jwt
import json
import unittest

from django.test    import TestCase, Client
from unittest.mock  import patch, MagicMock
from users.models   import User, Bank, BankAccount
from my_settings    import SECRET_KEY, ALGORITHM
from django.conf    import settings

class KakaoSocialLoginTest(TestCase):
    def setUp(self):
       user = User.objects.create(
            id        = 1,
            kakao_id  = 123456789,
            nickname  = "melody",
        )
        
    @patch("users.views.requests")
    def test_kakao_signin_new_user_success(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    "id": 123456789,
                    "connected_at": "2021-09-15T11:53:55Z",
                    "properties": {
                        "nickname": "\ud83c\udfb6melody\ud83c\udfb6"
                    }, 
                    "kakao_account": {
                        "profile_nickname_needs_agreement": False, 
                        "profile_image_needs_agreement": False, 
                        "profile": {
                            "nickname": "hello",
                            "thumbnail_image_url": "http://k.kakaocdn.net/dn/dpk9l1/btqmGhA2lKL/Oz0wDuJn1YV2DIn92f6DVK/img_110x110.jpg", 
                            "profile_image_url": "http://k.kakaocdn.net/dn/dpk9l1/btqmGhA2lKL/Oz0wDuJn1YV2DIn92f6DVK/img_640x640.jpg", 
                            "is_default_image": True
                            }, 
                        "has_email": True, 
                        "email_needs_agreement": False, 
                        "is_email_valid": True, 
                        "is_email_verified": True, 
                        "email": "melody7454@naver.com"
                    }
                }
                
        mocked_requests.post = MagicMock(return_value = MockedResponse())
        data = {"access_token": "fake_auth_key"}
        response = client.post("/users/signin", content_type="application/json", data=json.dumps(data))

        token = jwt.encode({"id": 1}, SECRET_KEY, algorithm=ALGORITHM)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"TOKEN": token})

    def tearDown(self):
        User.objects.all().delete()


class BankAccountViewTestGET(TestCase):
    def setUp(self):
        Bank.objects.create(
            id   = 1,
            name = "하나은행"
        )

        BankAccount.objects.create(
            id             = 1,
            account_number = "72491028234567",
            account_holder = "멜로디",
            bank_id        = Bank.objects.get(name="하나은행").id 
        )

        User.objects.create(
                id       = 1,
                kakao_id = 123,
                nickname = "Melody",
                bank_account_id = BankAccount.objects.get(id=1).id
        )
        User.objects.create(
                id       = 2,
                kakao_id = 456,
                nickname = "Mike",
        )
        
    def test_user_account_error(self):
        client   = Client()

        response = client.get('/users/bank_account/2')

        self.assertEqual(response.json(), {"ERROR" : "USER_HAS_NO_BANK_ACCOUNT"} )
        self.assertEqual(response.status_code, 404)

    def test_user_error(self):
        client   = Client()
        response = client.get('/users/bank_account/3')

        self.assertEqual(response.json(), {"ERROR" : "USER_DOES_NOT_EXIST"})
        self.assertEqual(response.status_code, 404)

    def test_user_account_get_success(self):
        client   = Client()
        response = client.get("/users/bank_account/1")
        
        self.assertEqual(response.json(),
            {
                "MESSAGE": {
                    "account_holder" : "멜로디",
                    "account_number" : "72491028234567",
                    "bank_name"      : "하나은행"
                }
            }
        )
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        BankAccount.objects.all().delete()
        User.objects.all().delete()

class BankAccountViewTestPOST(TestCase):
    def setUp(self):
        Bank.objects.create(
            id   = 1,
            name = "하나은행"
        )

        Bank.objects.create(
            id   = 2,
            name = "신한은행"
        )

        User.objects.create(
                id       = 1,
                kakao_id = 123,
                nickname = "Melody",
        )

        BankAccount.objects.create(
            id             = 1,
            account_number = "72491028234567",
            account_holder = "마이크",
            bank_id        = Bank.objects.get(name="하나은행").id 
        )

        User.objects.create(
                id              = 2,
                kakao_id        = 456,
                nickname        = "Mike",
                bank_account_id = BankAccount.objects.get(id=1).id
        )
        
    def test_user_error(self):
        client       = Client()
        access_token = jwt.encode({'id' : 2}, settings.SECRET_KEY, algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}        
        user_bank_account = {
            "account_holder" : "김또또",
            "account_number" : "4567898234452",
            "bank_name"      : "하나은행"
        }

        response = client.post("/users/bank_account/3",json.dumps(user_bank_account), content_type="application/json", **headers)
        self.assertEqual(response.json(), {"ERROR" : "USER_DOES_NOT_EXIST"} )
        self.assertEqual(response.status_code, 404)
    
    def test_account_number_error(self):
        client       = Client()
        access_token = jwt.encode({'id' : 2}, settings.SECRET_KEY, algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}        
        user_bank_account = {
            "account_holder" : "김또또",
            "account_number" : "45678-98234-452",
            "bank_name"      : "하나은행"
        }

        response = client.post("/users/bank_account/1",json.dumps(user_bank_account), content_type="application/json", **headers)
        self.assertEqual(response.json(), {"ERROR" : "DO_NOT_ENTER_STRING"} )
        self.assertEqual(response.status_code, 400)

    def test_bank_error(self):
        client       = Client()
        access_token = jwt.encode({'id' : 2}, settings.SECRET_KEY, algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}        
        user_bank_account = {
            "account_holder" : "김또또",
            "account_number" : "4567898234452",
            "bank_name"      : "부자은행"
        }

        response = client.post("/users/bank_account/1",json.dumps(user_bank_account), content_type="application/json", **headers)
        self.assertEqual(response.json(), {"ERROR" : "BANK_DOES_NOT_EXIST"})
        self.assertEqual(response.status_code, 400)

    def test_user_bank_account_update_post_success(self):
        client       = Client()
        access_token = jwt.encode({'id' : 2}, settings.SECRET_KEY, algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}        
        user_bank_account = {
            "account_holder" : "미케",
            "account_number" : "4567898234452",
            "bank_name"      : "신한은행"
        }

        response = client.post("/users/bank_account/2",json.dumps(user_bank_account), content_type="application/json", **headers)
        self.assertEqual(response.json(),{"MESSAGE" : "ACCOUNT'S_MODIFIED"})
        self.assertEqual(response.status_code, 200)

    def test_user_account_post_success(self):
        client       = Client()
        access_token = jwt.encode({'id' : 2}, settings.SECRET_KEY, algorithm='HS256')
        headers      = {"HTTP_Authorization": access_token}        
        user_bank_account = {
            "account_holder" : "김또또",
            "account_number" : "4567898234452",
            "bank_name"      : "하나은행"
        }

        response = client.post("/users/bank_account/1",json.dumps(user_bank_account), content_type="application/json", **headers)
        self.assertEqual(response.json(),{"MESSAGE" : "YOU_ARE_A_HOST_NOW"})
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        BankAccount.objects.all().delete()
        User.objects.all().delete()
