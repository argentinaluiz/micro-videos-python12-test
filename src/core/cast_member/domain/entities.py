from dataclasses import field
import datetime
from typing import Literal
from pydantic.dataclasses import dataclass
from pydantic import Field, Strict
from typing_extensions import Annotated
from core.shared.domain.entities import AggregateRoot
from core.shared.domain.value_objects import Uuid

class CastMemberId(Uuid):
    pass

_DIRECTOR = 1
_ACTOR = 2

CastMemberType = Literal[_DIRECTOR, _ACTOR] #type: ignore

@dataclass(slots=True, kw_only=True)
class CastMember(AggregateRoot):

    DIRECTOR = _DIRECTOR
    ACTOR = _ACTOR

    cast_member_id: CastMemberId = field(default_factory=CastMemberId)
    name: str = Field(max_length=255)
    type: CastMemberType
    created_at: Annotated[datetime.datetime, Strict()] = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC))

    @property
    def entity_id(self) -> Uuid:
        return self.cast_member_id

    def change_name(self, name: str):
        self.name = name
        self.validate()

    def change_type(self, _type: CastMemberType):
        self.type = _type
        self.validate()

    def validate(self):
        self._validate({
                'cast_member_id': self.cast_member_id,
                'name': self.name,
                'type': self.type,
                'created_at': self.created_at
        })

    @staticmethod
    def fake(): #type: ignore
        from .entities_fake_builder import CastMemberFakerBuilder # pylint: disable=import-outside-toplevel
        return CastMemberFakerBuilder #type: ignore
