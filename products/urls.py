from django.urls    import path

from products.views import ListCategoryView, LocationView,ProductDetailView, LikeView, ReviewView, UserProductView, ProductListView, MainPageCategoryView, ImageUploadView


urlpatterns = [
    path('products/host/<int:user_id>', UserProductView.as_view()),
    path('products/main_category/<int:main_category_id>', ListCategoryView.as_view()),
    path('product/<int:product_id>', ProductDetailView.as_view()),
    path('product/<int:product_id>/like', LikeView.as_view()),
    path('product/<int:product_id>/review', ReviewView.as_view()),
    path('products/main_page_category', MainPageCategoryView.as_view()),
    path('products/list/<int:main_category_id>', ProductListView.as_view()),
    path('product/<int:product_id>/location', LocationView.as_view()),
    path('product/<int:product_id>/host/<int:user_id>/image_upload', ImageUploadView.as_view()),
]
