import jwt
import json
import unittest

from django.test import TestCase, Client
 
from unittest.mock  import patch, MagicMock
from users.models import User
from my_settings  import SECRET_KEY, ALGORITHM

class KakaoSocialLoginTest(TestCase):
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