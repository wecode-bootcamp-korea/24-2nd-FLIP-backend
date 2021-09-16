from products.models import MainCategory, SubCategory
from django.test import TestCase, Client

class MainCategoryTest(TestCase):
    def setUp(self):
        main_category = MainCategory.objects.create(
            id        = 1,
            name      = "아웃도어",
            image_url = "https://images.ctfassets.net/hrltx12pl8hq/38KzANR5RR0lZ8jPlkOMwr/91b5342346b92bdf11c35a862e747d03/01-parks-outdoors_1661119069.jpg?fit=fill&w=480&h=270"
        )

        SubCategory.objects.create(
            id            = 1,
            name          = "서핑",
            main_category = main_category,
        )

    def tearDown(self):
        MainCategory.objects.all().delete()
        SubCategory.objects.all().delete()

    def test_listcategory_get_success(self):
        client  = Client()
        response = client.get("/products/main_category/1")
        self.assertEqual(response.json(),
            {
                "sub_category_list" : [
                    {
                        "sub_category_id" : 1,
                        "sub_category_name" : "서핑"
                    }
                ]
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_listcategory_get_error(self):
            client = Client()
            response = client.get('/products/main_category/20000')
            self.assertEqual(response.json(),
                {
                    'MESSAGE' : 'Non-Existing Main Category'
                }
            )
            self.assertEqual(response.status_code, 404)


