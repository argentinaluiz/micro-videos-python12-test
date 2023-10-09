

import abc
from dataclasses import dataclass, field
from typing import Any, Generic, List, Type, TypeVar
from core.shared.domain.entities import Entity
from core.shared.domain.exceptions import NotFoundException
from core.shared.domain.search_params import Filter, SearchParams, SearchResult, SortDirection
from core.shared.domain.value_objects import ValueObject


ET = TypeVar('ET', bound=Entity)
EntityId = TypeVar('EntityId', bound=ValueObject)


class IRepository(Generic[ET, EntityId], abc.ABC):

    @abc.abstractmethod
    def insert(self, entity: ET) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def bulk_insert(self, entities: List[ET]) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_by_id(self, entity_id: EntityId) -> ET | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_all(self) -> List[ET]:
        raise NotImplementedError()

    @abc.abstractmethod
    def update(self, entity: ET) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def delete(self, entity_id: EntityId) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_entity(self) -> Type[ET]:
        raise NotImplementedError()


class ISearchableRepository(
        Generic[ET, EntityId],
        IRepository[ET, EntityId], abc.ABC):

    sortable_fields: List[str] = []

    @abc.abstractmethod
    def search(self, input_params: Any) -> Any:
        raise NotImplementedError()


@dataclass(slots=True)
class InMemoryRepository(IRepository[ET, EntityId], abc.ABC):
    items: List[ET] = field(default_factory=lambda: [])

    def insert(self, entity: ET) -> None:
        self.items.append(entity)

    def bulk_insert(self, entities: List[ET]) -> None:
        self.items = entities + self.items

    def find_by_id(self, entity_id: EntityId) -> ET | None:
        return self._get(entity_id)

    def find_all(self) -> List[ET]:
        return self.items

    def update(self, entity: ET) -> None:
        entity_found = self._get(entity.entity_id)  # type: ignore

        if not entity_found:
            raise NotFoundException(
                entity.entity_id, str(self.get_entity().__class__))

        index = self.items.index(entity_found)
        self.items[index] = entity

    def delete(self, entity_id: EntityId) -> None:
        if entity_found := self._get(entity_id):
            self.items.remove(entity_found)
        else:
            raise NotFoundException(
                entity_id, str(self.get_entity().__class__))

    def _get(self, entity_id: EntityId) -> ET | None:
        return next(filter(lambda i: i.entity_id == entity_id, self.items), None)


@dataclass(slots=True)
class InMemorySearchableRepository(
    Generic[ET, EntityId, Filter],
    InMemoryRepository[ET, EntityId],
    ISearchableRepository[
        ET,
        EntityId,
    ],
    abc.ABC
):
    def search(self, input_params: SearchParams[Filter]) -> SearchResult[ET]:
        items_filtered = self._apply_filter(self.items, input_params.filter)
        items_sorted = self._apply_sort(
            items_filtered, input_params.sort, input_params.sort_dir)
        items_paginated = self._apply_paginate(
            items_sorted, input_params.page, input_params.per_page)

        return SearchResult(
            items=items_paginated,
            total=len(items_filtered),
            current_page=input_params.page,
            per_page=input_params.per_page,
        )

    @abc.abstractmethod
    def _apply_filter(self, items: List[ET], filter_param: Filter | None) -> List[ET]:
        raise NotImplementedError()

    def _apply_sort(self,
                    items: List[ET],
                    sort: str | None,
                    sort_dir: SortDirection | None) -> List[ET]:
        if sort and sort in self.sortable_fields:
            is_reverse = sort_dir == SortDirection.DESC
            return sorted(items, key=lambda item: getattr(item, sort), reverse=is_reverse)
        return items

    def _apply_paginate(self, items: List[ET], page: int, per_page: int) -> List[ET]:  # pylint: disable=useless-return
        start = (page - 1) * per_page
        limit = start + per_page
        return items[slice(start, limit)]
