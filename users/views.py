import json
from products.models import Location
import jwt
import requests

from django.views         import View
from django.http.response import JsonResponse
from datetime             import datetime, timedelta


from users.models import User, Bank, BankAccount
from products.models import Review, Location, MainCategory, Product, SubCategory, GatherLocation, ProductImage, UserLike

from my_settings  import SECRET_KEY, ALGORITHM

KAKAO_USER_INFORMATION_API ="https://kapi.kakao.com/v2/user/me"

class KakaoSignInView(View):
    def post(self, request):
        data = json.loads(request.body)
        access_token = data.get('access_token')
        
        if not access_token:
            return JsonResponse({"MESSAGE":"ACCESS_TOKEN_DOES_NOT_EXIST"}, status=400)
        
        profile_request = requests.post(KAKAO_USER_INFORMATION_API, headers={"Authorization" : f"Bearer {access_token}"})
        profile_json    = profile_request.json()

        kakao_account = profile_json.get('kakao_account')
        email         = kakao_account.get("email")
        profile       = kakao_account.get("profile")
        nick_name     = profile.get("nickname")
        profile_image = profile.get("profile_image_url")
        kakao_number  = profile_json.get('id')

        user, created = User.objects.get_or_create(
            kakao_id  = kakao_number,
            defaults  ={
                'nickname'  : nick_name,
                'email'     : email,
                'image_url' : profile_image
            }
        )

        kakao_user = User.objects.get(kakao_id=kakao_number)
        token      = jwt.encode({"id": kakao_user.id, 'exp':datetime.utcnow() + timedelta(days=2)}, SECRET_KEY, algorithm=ALGORITHM)

        return JsonResponse({"TOKEN": token}, status=200)