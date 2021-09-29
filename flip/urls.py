from django.urls import path, include

urlpatterns = [
    path('', include('products.urls')),
    path('users', include('users.urls')),
    path('products', include('products.urls'))
]
