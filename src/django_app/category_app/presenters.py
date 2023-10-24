from datetime import datetime
from typing import Annotated
from core.category.application.use_cases import CategoryOutput, ListCategoriesUseCase
from django_app.shared_app.presenters import CollectionPresenter, ResourcePresenter
from pydantic import PlainSerializer
from pydantic.dataclasses import dataclass


@dataclass(slots=True)
class CategoryPresenter(ResourcePresenter):
    id: str
    name: str
    description: str | None
    is_active: bool
    created_at: Annotated[datetime, PlainSerializer(lambda x: x.isoformat())]

    @classmethod
    def from_output(cls, output: CategoryOutput):
        return cls(
            id=output.id,
            name=output.name,
            description=output.description,
            is_active=output.is_active,
            created_at=output.created_at
        )


@dataclass(slots=True)
class CategoryCollectionPresenter(CollectionPresenter):
    output: ListCategoriesUseCase.Output

    def __post_init__(self):
        self.data = [
            CategoryPresenter(
                id=item.id,
                name=item.name,
                description=item.description,
                is_active=item.is_active,
                created_at=item.created_at
            ) for item in self.output.items
        ]
        self.pagination = self.output
