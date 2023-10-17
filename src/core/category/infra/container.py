from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer
from core.category.application.use_cases import (
    CreateCategoryUseCase, DeleteCategoryUseCase, GetCategoryUseCase, ListCategoriesUseCase, UpdateCategoryUseCase
)

from core.category.infra.repositories import CategoryInMemoryRepository
from django_app.category_app.models import CategoryDjangoRepository


class CategoryContainer(DeclarativeContainer):
    category_repository_in_memory = providers.Singleton( #type: ignore
        CategoryInMemoryRepository) #type: ignore

    category_repository_django_orm = providers.Singleton(
        CategoryDjangoRepository)

    list_categories_use_case = providers.Singleton(
        ListCategoriesUseCase,
        category_repo=category_repository_django_orm
    )

    get_category_use_case = providers.Singleton(
        GetCategoryUseCase,
        category_repo=category_repository_django_orm
    )

    create_category_use_case = providers.Singleton(
        CreateCategoryUseCase,
        category_repo=category_repository_django_orm
    )

    update_category_use_case = providers.Singleton(
        UpdateCategoryUseCase,
        category_repo=category_repository_django_orm
    )

    delete_category_use_case = providers.Singleton(
        DeleteCategoryUseCase,
        category_repo=category_repository_django_orm
    )
