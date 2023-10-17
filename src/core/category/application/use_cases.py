
from dataclasses import MISSING, dataclass as python_dataclass
from datetime import datetime
from typing import Annotated
from core.shared.domain.pydantic import StrNotEmpty
from pydantic import BeforeValidator, Field, StrictBool
from pydantic.dataclasses import dataclass as pydantic_dataclass
from core.category.domain.entities import Category
from core.category.domain.repositories import ICategoryRepository
from uuid import UUID
from core.shared.application.use_cases import PaginationOutput, SearchInput, UseCase
from core.shared.domain.exceptions import EntityValidationException, NotFoundException
from core.shared.domain.value_objects import Uuid


@python_dataclass(frozen=True, slots=True)
class CategoryOutput:
    id: str
    name: str
    description: str | None
    is_active: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, category: Category):
        return cls(
            id=category.category_id.id,
            name=category.name,
            description=category.description,
            is_active=category.is_active,
            created_at=category.created_at
        )


@python_dataclass(slots=True, frozen=True)
class CreateCategoryUseCase(UseCase):

    category_repo: ICategoryRepository

    def execute(self, input_param: 'Input') -> 'Output':
        category = Category(
            name=input_param.name,
            description=input_param.description,
            is_active=input_param.is_active
        )
        self.category_repo.insert(category)
        return self.__to_output(category)

    def __to_output(self, category: Category):
        return self.Output.from_entity(category)

    @pydantic_dataclass(slots=True, frozen=True)
    class Input:
        name: Annotated[str, StrNotEmpty]
        description: Annotated[str | None, StrNotEmpty] = None
        is_active: StrictBool = True

    @python_dataclass(slots=True, frozen=True)
    class Output(CategoryOutput):
        pass


@python_dataclass(slots=True, frozen=True)
class GetCategoryUseCase(UseCase):

    category_repo: ICategoryRepository

    def execute(self, input_param: 'Input') -> 'Output':
        category_id = Uuid(str(input_param.id))
        if category := self.category_repo.find_by_id(category_id):
            return self.__to_output(category)
        else:
            raise NotFoundException(str(input_param.id), Category.__name__)

    def __to_output(self, category: Category):
        return self.Output.from_entity(category)

    @pydantic_dataclass(slots=True, frozen=True)
    class Input:
        id: UUID  # accepts uuid string

    @python_dataclass(slots=True, frozen=True)
    class Output(CategoryOutput):
        pass


@python_dataclass(slots=True, frozen=True)
class ListCategoriesUseCase(UseCase):

    category_repo: ICategoryRepository

    def execute(self, input_param: 'Input') -> 'Output':
        search_params = self.category_repo.SearchParams(
            **input_param.to_repository_input())
        result = self.category_repo.search(search_params)
        return self.__to_output(result)

    def __to_output(self, result: ICategoryRepository.SearchResult):  # pylint: disable=no-self-use
        items = list(
            map(CategoryOutput.from_entity, result.items)
        )
        return self.Output.from_search_result(
            result,
            items,
        )

    @pydantic_dataclass(slots=True, frozen=True)
    class Input(SearchInput[str]):
        pass

    @python_dataclass(slots=True, frozen=True)
    class Output(PaginationOutput[CategoryOutput]):
        pass


@python_dataclass(slots=True, frozen=True)
class UpdateCategoryUseCase(UseCase):

    category_repo: ICategoryRepository

    def execute(self, input_param: 'Input') -> 'Output':
        category_id = Uuid(str(input_param.id))
        entity = self.category_repo.find_by_id(category_id)

        if entity is None:
            raise NotFoundException(str(input_param.id), Category.__name__)

        if input_param.name is not None:
            entity.change_name(input_param.name)

        if input_param.description != MISSING:  # type: ignore
            entity.change_description(input_param.description)

        if input_param.is_active is True:
            entity.activate()

        if input_param.is_active is False:
            entity.deactivate()
        
        if entity.notification.has_errors():
            raise EntityValidationException(entity.notification.errors)

        self.category_repo.update(entity)
        return self.__to_output(entity)

    def __to_output(self, category: Category) -> 'Output':
        return self.Output.from_entity(category)

    @pydantic_dataclass(slots=True, frozen=True)
    class Input:
        id: UUID  # accepts uuid string
        name: Annotated[str | None, StrNotEmpty] = None
        description: Annotated[str | None, StrNotEmpty] = Field(default=MISSING)  # type: ignore
        is_active: StrictBool | None = None

    @python_dataclass(slots=True, frozen=True)
    class Output(CategoryOutput):
        pass


@python_dataclass(slots=True, frozen=True)
class DeleteCategoryUseCase(UseCase):

    category_repo: ICategoryRepository

    def execute(self, input_param: 'Input') -> None:
        category_id = Uuid(str(input_param.id))
        self.category_repo.delete(category_id)

    @pydantic_dataclass(slots=True, frozen=True)
    class Input:
        id: UUID
