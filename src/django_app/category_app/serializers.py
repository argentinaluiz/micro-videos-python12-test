from abc import ABC
from dataclasses import field
from datetime import datetime
from typing import Annotated, Any, List
from core.category.application.use_cases import CategoryOutput, ListCategoriesUseCase
from core.shared.application.use_cases import PaginationOutput
from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, TypeAdapter
from pydantic.dataclasses import dataclass


class ResourcePresenter(ABC):  # (BaseModel):

    # def serialize(self):
    #     return self.model_dump()

    def serialize(self):
        data = TypeAdapter(self.__class__).dump_python(self)
        return {'data': data}


@dataclass(slots=True)
class CollectionPresenter(ABC):
    data: List[Any] = field(init=False)
    pagination: PaginationOutput[Any] | None = field(init=False, default=None)

    def serialize(self):
        print(self.pagination)
        data = [TypeAdapter(item.__class__).dump_python(item)
                for item in self.data]
        meta = {
            'total': self.pagination.total,
            'current_page': self.pagination.current_page,
            'per_page': self.pagination.per_page,
            'last_page': self.pagination.last_page
        } if self.pagination is not None else None
        return {
            'data': data,
            'meta': meta
        }


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