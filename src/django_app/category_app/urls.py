
from django.urls import path 
from django_app.category_app.api import CategoryController
from django_app.ioc_app.containers import container


def __init_category_controller():
    return {
        'create_use_case': container.category.create_category_use_case,
        'list_use_case': container.category.list_categories_use_case,
        'get_use_case': container.category.get_category_use_case,
        'update_use_case': container.category.update_category_use_case,
        'delete_use_case': container.category.delete_category_use_case,
    }


urlpatterns = [
    path('categories/', CategoryController.as_view(
        **__init_category_controller()
    )),
    path('categories/<category_id>/', CategoryController.as_view(
        **__init_category_controller()
    )),
]
