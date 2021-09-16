from django.urls import path

from .views      import PrivateDetailView

urlpatterns = [
    path('/product/<int:product_id>', PrivateDetailView.as_view())
]
