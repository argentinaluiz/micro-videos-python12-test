
from dataclasses import MISSING, dataclass as python_dataclass
from datetime import datetime
from typing import Annotated
from core.shared.domain.pydantic import StrNotEmpty
from pydantic import StrictBool
from pydantic.dataclasses import dataclass as pydantic_dataclass
from core.cast_member.domain.entities import CastMember, CastMemberId, CastMemberType
from core.cast_member.domain.repositories import CastMemberFilter, ICastMemberRepository
from uuid import UUID
from core.shared.application.use_cases import PaginationOutput, SearchInput, UseCase
from core.shared.domain.exceptions import EntityValidationException, NotFoundException


@python_dataclass(frozen=True, slots=True)
class CastMemberOutput:
    id: str
    name: str
    type: CastMemberType
    created_at: datetime

    @classmethod
    def from_entity(cls, cast_member: CastMember):
        return cls(
            id=cast_member.cast_member_id.id,
            name=cast_member.name,
            type=cast_member.type,
            created_at=cast_member.created_at
        )


@python_dataclass(slots=True, frozen=True)
class CreateCastMemberUseCase(UseCase):

    cast_member_repo: ICastMemberRepository

    def execute(self, input_param: 'Input') -> 'Output':
        cast_member = CastMember(
            name=input_param.name,
            type=input_param.type,
        )
        self.cast_member_repo.insert(cast_member)
        return self.__to_output(cast_member)

    def __to_output(self, category: CastMember):
        return self.Output.from_entity(category)

    @pydantic_dataclass(slots=True, frozen=True)
    class Input:
        name: Annotated[str, StrNotEmpty]
        type: CastMemberType

    @python_dataclass(slots=True, frozen=True)
    class Output(CastMemberOutput):
        pass


@python_dataclass(slots=True, frozen=True)
class GetCastMemberUseCase(UseCase):

    cast_member_repo: ICastMemberRepository

    def execute(self, input_param: 'Input') -> 'Output':
        cast_member_id = CastMemberId(str(input_param.id))
        if cast_member := self.cast_member_repo.find_by_id(cast_member_id):
            return self.__to_output(cast_member)
        else:
            raise NotFoundException(str(input_param.id), CastMember.__name__)

    def __to_output(self, category: CastMember):
        return self.Output.from_entity(category)

    @pydantic_dataclass(slots=True, frozen=True)
    class Input:
        id: UUID  # accepts uuid string

    @python_dataclass(slots=True, frozen=True)
    class Output(CastMemberOutput):
        pass


@python_dataclass(slots=True, frozen=True)
class ListCastMembersUseCase(UseCase):

    cast_member_repo: ICastMemberRepository

    def execute(self, input_param: 'Input') -> 'Output':
        
        search_params = self.cast_member_repo.SearchParams(
            **input_param.to_repository_input()) # type: ignore
        result = self.cast_member_repo.search(search_params)
        return self.__to_output(result)

    def __to_output(self, result: ICastMemberRepository.SearchResult):  # pylint: disable=no-self-use
        items = list(
            map(CastMemberOutput.from_entity, result.items)
        )
        return self.Output.from_search_result(
            result,
            items,
        )

    @pydantic_dataclass(slots=True, frozen=True)
    class Input(SearchInput[CastMemberFilter]):
        pass

    @python_dataclass(slots=True, frozen=True)
    class Output(PaginationOutput[CastMemberOutput]):
        pass


@python_dataclass(slots=True, frozen=True)
class UpdateCastMemberUseCase(UseCase):

    cast_member_repo: ICastMemberRepository

    def execute(self, input_param: 'Input') -> 'Output':
        category_id = CastMemberId(str(input_param.id))
        entity = self.cast_member_repo.find_by_id(category_id)

        if entity is None:
            raise NotFoundException(str(input_param.id), CastMember.__name__)

        if input_param.name is not None:
            entity.change_name(input_param.name)

        if input_param.type is not None:
            entity.change_type(input_param.type)

        if entity.notification.has_errors():
            raise EntityValidationException(entity.notification.errors)

        self.cast_member_repo.update(entity)
        return self.__to_output(entity)

    def __to_output(self, cast_member: CastMember) -> 'Output':
        return self.Output.from_entity(cast_member)

    @pydantic_dataclass(slots=True, frozen=True)
    class Input:
        id: UUID  # accepts uuid string
        name: Annotated[str | None, StrNotEmpty] = None
        type: CastMemberType = None
        is_active: StrictBool | None = None

    @python_dataclass(slots=True, frozen=True)
    class Output(CastMemberOutput):
        pass


@python_dataclass(slots=True, frozen=True)
class DeleteCastMemberUseCase(UseCase):

    cast_member_repo: ICastMemberRepository

    def execute(self, input_param: 'Input') -> None:
        category_id = CastMemberId(str(input_param.id))
        self.cast_member_repo.delete(category_id)

    @pydantic_dataclass(slots=True, frozen=True)
    class Input:
        id: UUID
