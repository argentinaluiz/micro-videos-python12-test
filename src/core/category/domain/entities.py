from dataclasses import field
import datetime
from pydantic.dataclasses import dataclass
from pydantic import Field, Strict, StrictBool, ValidationError
from typing_extensions import Annotated
from core.shared.domain.entities import Entity
from core.shared.domain.value_objects import Uuid

@dataclass(slots=True, kw_only=True)
class Category(Entity):
    category_id: Uuid = field(default_factory=Uuid)
    name: str = Field(max_length=255)
    description: str | None = None
    is_active: StrictBool = True
    created_at: Annotated[datetime.datetime, Strict()] = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC))

    @property
    def entity_id(self) -> Uuid:
        return self.category_id

    def change_name(self, name: str):
        self.name = name
        self.validate()

    def change_description(self, description: str | None):
        self.description = description
        self.validate()

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def validate(self):
        self._validate({
                'category_id': self.category_id,
                'name': self.name,
                'description': self.description,
                'is_active': self.is_active,
                'created_at': self.created_at
        })

    @staticmethod
    def fake(): #type: ignore
        from .entities_fake_builder import CategoryFakerBuilder # pylint: disable=import-outside-toplevel
        return CategoryFakerBuilder #type: ignore
