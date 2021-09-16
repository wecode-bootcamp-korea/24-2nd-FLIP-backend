from django.urls import path

from .views      import PublicDetailView

urlpatterns = [
    path('/product/<int:product_id>', PublicDetailView.as_view())
]
