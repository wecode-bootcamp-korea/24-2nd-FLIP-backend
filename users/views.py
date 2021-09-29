import jwt
import json
import requests

from datetime             import datetime, timedelta
from django.views         import View
from django.http.response import JsonResponse

from users.decorator import login_decorator
from users.models    import User, Bank, BankAccount
from my_settings     import SECRET_KEY, ALGORITHM

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
            defaults  = {
                'nickname' :nick_name,
                'email'    :email,
                'image_url':profile_image
            }
        )

        kakao_user = User.objects.get(kakao_id=kakao_number)
        token      = jwt.encode({"id": kakao_user.id, 'exp':datetime.utcnow() + timedelta(days=2)}, SECRET_KEY, algorithm=ALGORITHM)

        return JsonResponse({"TOKEN": token}, status=200)

@login_decorator
class BankAccountView(View):
    def post(self, request, user_id):
        try:
            data           = json.loads(request.body)
            account_holder = data["account_holder"]
            account_number = data["account_number"]

            if not User.objects.filter(id=user_id).exists(): 
                return JsonResponse({"ERROR" : "USER_DOES_NOT_EXIST"}, status=404)
            
            user         = User.objects.get(id=user_id)
            user_account = user.bank_account

            for i in account_number:
                if i == "-":
                    return JsonResponse({"ERROR" : "DO_NOT_ENTER_STRING"}, status=400)

            if not Bank.objects.filter(name=data["bank_name"]).exists(): 
                return JsonResponse({"ERROR" : "BANK_DOES_NOT_EXIST"}, status=400)

            bank = Bank.objects.get(name=data["bank_name"])
            
            if user_account:
                user_account.account_holder = account_holder
                user_account.account_number = account_number
                user_account.bank_id        = bank.id
                user_account.save()
                return JsonResponse({"MESSAGE":"ACCOUNT'S_MODIFIED"}, status=200)
            
            account, created = BankAccount.objects.get_or_create(
                account_holder = account_holder,
                account_number = account_number,
                bank_id        = bank.id
            )
            user.bank_account = account
            user.save()
            
            return JsonResponse({"MESSAGE" : "YOU_ARE_A_HOST_NOW"}, status=200)
        except KeyError:
            return JsonResponse({"ERROR" : "KEY_ERROR"}, status=400)
        except ValueError:
            return JsonResponse({"ERROR" : "VALUE_ERROR"}, status=400)

    def get(self, request, user_id):
        if not User.objects.filter(id=user_id).exists():
            return JsonResponse({"ERROR" : "USER_DOES_NOT_EXIST"}, status=404)

        user_account = User.objects.get(id=user_id).bank_account
        
        if not user_account:
            return JsonResponse({"ERROR" : "USER_HAS_NO_BANK_ACCOUNT"}, status=404)

        bank_account = {
            "account_holder" : user_account.account_holder,
            "account_number" : user_account.account_number,
            "bank_name"      : user_account.bank.name
        }

        return JsonResponse({"MESSAGE" : bank_account}, status=200)
