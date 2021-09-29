from django.urls import path

from users.views import KakaoSignInView, BankAccountView

urlpatterns = [
    path('/signin', KakaoSignInView.as_view()),
    path('/bank_account/<int:user_id>',BankAccountView.as_view())
]