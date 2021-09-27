from django.urls    import path

from products.views import ListCategoryView,ProductDetailView, LikeView, ReviewView

urlpatterns = [
    path('products/main_category/<int:main_category_id>', ListCategoryView.as_view()),
    path('product/<int:product_id>', ProductDetailView.as_view()),
    path('product/<int:product_id>/like', LikeView.as_view()),
    path('product/<int:product_id>/review', ReviewView.as_view())
]
