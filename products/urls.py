from django.urls    import path

from products.views import ListCategoryView

urlpatterns = [
    path('/main_category/<int:main_category_id>', ListCategoryView.as_view())
]