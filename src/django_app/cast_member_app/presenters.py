from datetime import datetime
from typing import Annotated
from core.cast_member.application.use_cases import CastMemberOutput, ListCastMembersUseCase
from core.cast_member.domain.entities import CastMemberType
from django_app.shared_app.presenters import CollectionPresenter, ResourcePresenter
from pydantic import PlainSerializer
from pydantic.dataclasses import dataclass


@dataclass(slots=True)
class CastMemberPresenter(ResourcePresenter):
    id: str
    name: str
    type: CastMemberType
    created_at: Annotated[datetime, PlainSerializer(lambda x: x.isoformat())]

    @classmethod
    def from_output(cls, output: CastMemberOutput):
        return cls(
            id=output.id,
            name=output.name,
            type=output.type,
            created_at=output.created_at
        )


@dataclass(slots=True)
class CastMemberCollectionPresenter(CollectionPresenter):
    output: ListCastMembersUseCase.Output

    def __post_init__(self):
        self.data = [
            CastMemberPresenter(
                id=item.id,
                name=item.name,
                type=item.type,
                created_at=item.created_at
            ) for item in self.output.items
        ]
        self.pagination = self.output
