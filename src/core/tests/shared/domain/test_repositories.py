from dataclasses import dataclass
from typing import Any, List
from unittest import TestCase, mock
from core.shared.domain.repositories import InMemoryRepository, InMemorySearchableRepository
from core.shared.domain.entities import Entity
from core.shared.domain.search_params import SearchParams, SearchResult, SortDirection
from core.shared.domain.value_objects import Uuid, ValueObject
import pytest


@dataclass(slots=True)
class StubEntity(Entity):
    id: Uuid
    name: str

    @property
    def entity_id(self) -> Uuid:
        return self.id


class StubInMemoryRepository(InMemoryRepository[StubEntity, Uuid]):
    def get_entity(self):
        return StubEntity


class TestInMemoryRepository:

    repository: StubInMemoryRepository

    def setup_method(self):
        self.repository = StubInMemoryRepository()

    def test_insert(self):
        entity = StubEntity(Uuid(), 'Test Entity')
        self.repository.insert(entity)
        assert entity in self.repository.items

    def test_bulk_insert(self):
        entities = [StubEntity(Uuid(), 'Test Entity') for _ in range(3)]
        self.repository.bulk_insert(entities)
        assert all(entity in self.repository.items for entity in entities)

    def test_find_by_id(self):
        entity = StubEntity(Uuid(), 'Test Entity')
        self.repository.insert(entity)
        found_entity = self.repository.find_by_id(entity.id)
        assert entity == found_entity

        assert self.repository.find_by_id(Uuid()) is None

    def test_find_by_id_not_found(self):
        entity_id = Uuid()
        found_entity = self.repository.find_by_id(entity_id)
        assert found_entity is None

    def test_find_all(self):
        entities = [StubEntity(Uuid(), 'Test Entity') for _ in range(3)]
        self.repository.bulk_insert(entities)
        found_entities = self.repository.find_all()
        assert all(entity in found_entities for entity in entities)

    def test_throw_exception_when_update_an_entity_not_found(self):
        entity = StubEntity(Uuid(), 'Test Entity')
        with pytest.raises(Exception):
            self.repository.update(entity)

    def test_update(self):
        entity = StubEntity(Uuid(), 'Test Entity')
        self.repository.insert(entity)
        entity.name = 'new value'
        self.repository.update(entity)
        found_entity = self.repository.find_by_id(entity.id)
        assert found_entity == entity

    def test_throw_exception_when_delete_an_entity_not_found(self):
        entity_id = Uuid()
        with pytest.raises(Exception):
            self.repository.delete(entity_id)

    def test_delete(self):
        entity = StubEntity(Uuid(), 'Test Entity')
        self.repository.insert(entity)
        self.repository.delete(entity.id)
        found_entity = self.repository.find_by_id(entity.id)
        assert found_entity is None

    def test_get_entity(self):
        entity = self.repository.get_entity()
        assert entity == StubEntity


@dataclass(slots=True)
class StubInMemorySearchableRepository(InMemorySearchableRepository[StubEntity, Uuid, str]):

    sortable_fields = ['name']

    def _apply_filter(self, items: List[StubEntity], filter_param: str | None) -> List[StubEntity]:
        if filter_param:
            filter_obj = filter(lambda i: filter_param.lower()
                                in i.name.lower(), items)
            return list(filter_obj)
        return items

    def get_entity(self):
        return StubEntity


class TestInMemorySearchableRepository:

    repository: StubInMemorySearchableRepository

    def setup_method(self):
        self.repository = StubInMemorySearchableRepository()

    def test__apply_filter(self):
        items = [StubEntity(Uuid(), 'test')]
        result = self.repository._apply_filter(  # pylint: disable=protected-access # type: ignore
            items, None)
        assert result == items

        items = [
            StubEntity(Uuid(), 'test'),
            StubEntity(Uuid(), 'TEST'),
            StubEntity(Uuid(), 'fake'),
        ]

        result = self.repository._apply_filter(  # pylint: disable=protected-access # type: ignore
            items, 'TEST')
        assert result == [items[0], items[1]]

    def test__apply_sort(self):
        items = [
            StubEntity(Uuid(), 'b'),
            StubEntity(Uuid(), 'a'),
            StubEntity(Uuid(), 'c'),
        ]

        result = self.repository._apply_sort(  # pylint: disable=protected-access # type: ignore
            items, 'name', SortDirection.ASC)
        assert result == [items[1], items[0], items[2]]

        result = self.repository._apply_sort(  # pylint: disable=protected-access # type: ignore
            items, 'name', SortDirection.DESC)
        assert result == [items[2], items[0], items[1]]

    def test__apply_paginate(self):
        items = [
            StubEntity(Uuid(), 'a'),
            StubEntity(Uuid(), 'b'),
            StubEntity(Uuid(), 'c'),
            StubEntity(Uuid(), 'd'),
            StubEntity(Uuid(), 'e'),
        ]

        result = self.repository._apply_paginate(  # pylint: disable=protected-access # type: ignore
            items, 1, 2)
        assert result == [items[0], items[1]]

        result = self.repository._apply_paginate(  # pylint: disable=protected-access # type: ignore
            items, 2, 2)
        assert result == [items[2], items[3]]

        result = self.repository._apply_paginate(  # pylint: disable=protected-access # type: ignore
            items, 3, 2)
        assert result == [items[4]]

        result = self.repository._apply_paginate(  # pylint: disable=protected-access # type: ignore
            items, 4, 2)
        assert result == []

    def test_search_when_params_is_empty(self):
        entity = StubEntity(Uuid(), 'a')
        items = [entity] * 16
        self.repository.bulk_insert(items)

        result = self.repository.search(SearchParams())
        assert result == SearchResult(
            items=[entity] * 15,
            total=16,
            current_page=1,
            per_page=15,
        )

    def test_search_applying_filter_and_paginate(self):
        items = [
            StubEntity(Uuid(), 'test'),
            StubEntity(Uuid(), 'a'),
            StubEntity(Uuid(), 'TEST'),
            StubEntity(Uuid(), 'TeSt'),
        ]
        self.repository.bulk_insert(items)

        result = self.repository.search(SearchParams(
            init_page=1, init_per_page=2, init_filter='TEST'
        ))
        assert result == SearchResult(
            items=[items[0], items[2]],
            total=3,
            current_page=1,
            per_page=2,
        )

        result = self.repository.search(SearchParams(
            init_page=2, init_per_page=2, init_filter='TEST'
        ))
        assert result == SearchResult(
            items=[items[3]],
            total=3,
            current_page=2,
            per_page=2,
        )

        result = self.repository.search(SearchParams(
            init_page=3, init_per_page=2, init_filter='TEST'
        ))
        assert result == SearchResult[Any](
            items=[],
            total=3,
            current_page=3,
            per_page=2,
        )

    @pytest.mark.parametrize('search_params, expected_search_output', [
        pytest.param(
            SearchParams[str](
                init_page=1, init_per_page=2, init_sort='name'
            ),
            SearchResult[StubEntity](
                items=[1, 0],
                total=5,
                current_page=1,
                per_page=2,
            ),
            id='asc page 1'
        ),
        pytest.param(
            SearchParams[str](
                init_page=2, init_per_page=2, init_sort='name'
            ),
            SearchResult[StubEntity](
                items=[4, 2],
                total=5,
                current_page=2,
                per_page=2,
            ),
            id='asc page 2'
        ),
        pytest.param(
            SearchParams[str](
                init_page=3, init_per_page=2, init_sort='name'
            ),
            SearchResult[StubEntity](
                items=[3],
                total=5,
                current_page=3,
                per_page=2,
            ),
            id='asc page 3'
        ),
        pytest.param(
            SearchParams[str](
                init_page=1, init_per_page=2, init_sort='name', init_sort_dir=SortDirection.DESC
            ),
            SearchResult[StubEntity](
                items=[3, 2],
                total=5,
                current_page=1,
                per_page=2,
            ),
            id='desc page 1'
        ),
        pytest.param(
            SearchParams[str](
                init_page=2, init_per_page=2, init_sort='name', init_sort_dir=SortDirection.DESC
            ),
            SearchResult[StubEntity](
                items=[4, 0],
                total=5,
                current_page=2,
                per_page=2,
            ),
            id='desc page 2'
        ),
        pytest.param(
            SearchParams[str](
                init_page=3, init_per_page=2, init_sort='name', init_sort_dir=SortDirection.DESC
            ),
            SearchResult[StubEntity](
                items=[1],
                total=5,
                current_page=3,
                per_page=2,
            ),
            id='desc page 3'
        ),
    ])
    def test_search_applying_sort_and_paginate(self,
                                               search_params: SearchParams[str],
                                               expected_search_output: SearchResult[StubEntity]):
        items = [
            StubEntity(Uuid(), 'b'),
            StubEntity(Uuid(), 'a'),
            StubEntity(Uuid(), 'd'),
            StubEntity(Uuid(), 'e'),
            StubEntity(Uuid(), 'c'),
        ]
        self.repository.bulk_insert(items)

        result = self.repository.search(search_params)
        expected_search_output.items = [items[i]
                                        for i in expected_search_output.items]
        assert result == expected_search_output

    def test_search_applying_filter_and_sort_and_paginate(self):
        items = [
            StubEntity(Uuid(),'test'),
            StubEntity(Uuid(),'a'),
            StubEntity(Uuid(),'TEST'),
            StubEntity(Uuid(),'e'),
            StubEntity(Uuid(),'TeSt'),
        ]
        self.repository.bulk_insert(items)

        result = self.repository.search(SearchParams[str](
            init_page=1, init_per_page=2, init_sort='name', init_filter='TEST'
        ))
        assert result == SearchResult[StubEntity](
            items=[items[2], items[4]],
            total=3,
            current_page=1,
            per_page=2,
        )

        result = self.repository.search(SearchParams[str](
            init_page=2, init_per_page=2, init_sort='name', init_filter='TEST'
        ))
        assert result == SearchResult[StubEntity](
            items=[items[0]],
            total=3,
            current_page=2,
            per_page=2,
        )