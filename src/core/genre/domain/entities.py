from dataclasses import field
import datetime
from typing import List, Set
from core.category.domain.entities import CategoryId
from pydantic.dataclasses import dataclass
from pydantic import Field, Strict, StrictBool
from typing_extensions import Annotated
from core.shared.domain.entities import AggregateRoot
from core.shared.domain.value_objects import Uuid


class GenreId(Uuid):
    pass


@dataclass(slots=True, kw_only=True)
class Genre(AggregateRoot):

    genre_id: GenreId = field(default_factory=GenreId)
    name: str = Field(max_length=255)
    categories_id: Set[CategoryId] = Field(min_length=1)
    is_active: StrictBool = True
    created_at: Annotated[datetime.datetime, Strict()] = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC))

    @property
    def entity_id(self) -> Uuid:
        return self.genre_id

    def change_name(self, name: str):
        self.name = name
        self.validate()

    def add_category_id(self, category_id: CategoryId):
        self.categories_id.add(category_id)
        self.validate()

    def remove_category_id(self, category_id: CategoryId):
        self.categories_id.remove(category_id)
        self.validate()

    def sync_categories_id(self, categories_id: Set[CategoryId]):
        self.categories_id = categories_id
        self.validate()

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def validate(self):
        self._validate({
            'genre_id': self.genre_id,
            'name': self.name,
            'categories_id': self.categories_id,
            'created_at': self.created_at
        })

    @staticmethod
    def fake():  # type: ignore
        from .entities_fake_builder import GenreFakerBuilder  # pylint: disable=import-outside-toplevel
        return GenreFakerBuilder  # type: ignore
