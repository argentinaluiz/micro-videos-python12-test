

from datetime import datetime
from core.category.application.use_cases import CategoryOutput, ListCategoriesUseCase

from pydantic import TypeAdapter
from django_app.category_app.serializers import CategoryCollectionPresenter, CategoryPresenter, CollectionPresenter


def test_xpto():
    presenter = CategoryPresenter(
        id='1',
        name='name',
        description='description',
        is_active=True,
        created_at=datetime.now()
    )
    json = presenter.serialize()
    print(json)

    collection = CategoryCollectionPresenter(
        ListCategoriesUseCase.Output(
            items=[
                CategoryOutput(
                    id='1',
                    name='name',
                    description='description',
                    is_active=True,
                    created_at=datetime.now()
                )
            ],
            current_page=1,
            per_page=1,
            total=1,
            last_page=1
        )
    )
