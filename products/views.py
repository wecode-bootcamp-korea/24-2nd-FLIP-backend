import json
from unittest.main import main

from django.http     import JsonResponse
from django.views    import View

from products.models import MainCategory, SubCategory

class ListCategoryView(View):
    def get(self, request, main_category_id):
        try:
            if not MainCategory.objects.filter(id=main_category_id).exists():
                return JsonResponse({'MESSAGE':'Non-Existing Main Category'}, status=404)

            sub_category_list = [
                {
                    'sub_category_id' : sub_category.id,
                    'sub_category_name' : sub_category.name
                } for sub_category in SubCategory.objects.filter(main_category_id = main_category_id)
            ]
            return JsonResponse({'sub_category_list':sub_category_list}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status=400)

        except ValueError:
            return JsonResponse({'MESSAGE':'VALUE_ERROR'}, status=400)
