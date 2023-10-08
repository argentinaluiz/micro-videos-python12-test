from dataclasses import InitVar

import pytest
from core.shared.domain.search_params import ET, SearchParams, SearchResult, SortDirection, Filter, SortDirectionValues
from typing import List, Optional, Any


class TestSearchParams:

    def test_props_annotations(self):
        annotations = SearchParams.__annotations__
        assert annotations.keys() == {
            'page',
            'per_page',
            'sort',
            'sort_dir',
            'filter',
            'init_page',
            'init_per_page',
            'init_sort',
            'init_sort_dir',
            'init_filter'
        }
        assert annotations['page'] == int
        assert annotations['per_page'] == int
        assert annotations['sort'] == Optional[str]
        assert annotations['sort_dir'] == Optional[SortDirection]
        assert annotations['filter'] == Optional[Filter]  # type: ignore

        # must convert to string because a bug in pytest
        assert str(annotations['init_page']) == str(InitVar[int | None])
        assert str(annotations['init_per_page']) == str(InitVar[int | None])
        assert str(annotations['init_sort']) == str(InitVar[str | None])
        assert str(annotations['init_sort_dir']
                   ) == InitVar[SortDirectionValues | SortDirection | None].__repr__()
        assert str(annotations['init_filter']) == str(
            InitVar[Filter | None])  # type: ignore

    def test_default_values(self):
        params = SearchParams()  # type: ignore
        assert params.page == 1
        assert params.per_page == 15
        assert params.sort is None
        assert params.sort_dir is None
        assert params.filter is None  # type: ignore

    @pytest.mark.parametrize('page, expected', [
        pytest.param(None, 1, id='None'),
        pytest.param("", 1, id='empty string'),
        pytest.param("fake", 1, id='fake string'),
        pytest.param(0, 1, id='zero'),
        pytest.param(-1, 1, id='negative'),
        pytest.param("0", 1, id='zero string'),
        pytest.param("-1", 1, id='negative string'),
        pytest.param(5.5, 5, id='float'),
        pytest.param(True, 1, id='True'),
        pytest.param(False, 1, id='False'),
        pytest.param({}, 1, id='dict'),
        pytest.param(1, 1, id='int'),
        pytest.param(2, 2, id='int'),
    ])
    def test_page_prop(self, page: Any, expected: int):
        params = SearchParams(init_page=page)  # type: ignore
        assert params.page == expected

    @pytest.mark.parametrize('per_page, expected', [
        pytest.param(None, 15, id='None'),
        pytest.param("", 15, id='empty string'),
        pytest.param("fake", 15, id='fake string'),
        pytest.param(0, 15, id='zero'),
        pytest.param(-1, 15, id='negative'),
        pytest.param("0", 15, id='zero string'),
        pytest.param("-1", 15, id='negative string'),
        pytest.param(5.5, 5, id='float'),
        pytest.param(True, 1, id='True'),
        pytest.param(False, 15, id='False'),
        pytest.param({}, 15, id='dict'),
        pytest.param(1, 1, id='int'),
        pytest.param(2, 2, id='int'),
    ])
    def test_per_page_prop(self, per_page: Any, expected: int):
        params = SearchParams(init_per_page=per_page)  # type: ignore
        assert params.per_page == expected

    @pytest.mark.parametrize('sort, expected', [
        pytest.param(None, None, id='None'),
        pytest.param("", None, id='empty string'),
        pytest.param("fake", 'fake', id='fake string'),
        pytest.param(0, '0', id='zero'),
        pytest.param(-1, '-1', id='negative'),
        pytest.param("0", '0', id='zero string'),
        pytest.param("-1", '-1', id='negative string'),
        pytest.param(5.5, '5.5', id='float'),
        pytest.param(True, 'True', id='True'),
        pytest.param(False, 'False', id='False'),
        pytest.param({}, '{}', id='dict'),
    ])
    def test_sort_prop(self, sort: Any, expected: str | None):
        params = SearchParams(init_sort=sort)  # type: ignore
        assert params.sort == expected

    @pytest.mark.parametrize('sort_dir, expected', [
        pytest.param(None, SortDirection.ASC, id='None'),
        pytest.param("", SortDirection.ASC, id='empty string'),
        pytest.param("fake", SortDirection.ASC, id='fake string'),
        pytest.param(0, SortDirection.ASC, id='zero'),
        pytest.param({}, SortDirection.ASC, id='dict'),
        pytest.param('asc', SortDirection.ASC, id='asc'),
        pytest.param('ASC', SortDirection.ASC, id='ASC'),
        pytest.param('desc', SortDirection.DESC, id='desc'),
        pytest.param('DESC', SortDirection.DESC, id='DESC'),
    ])
    def test_sort_dir_prop(self, sort_dir: Any, expected: str | None):
        params = SearchParams(  # type: ignore
            init_sort='name', init_sort_dir=sort_dir)
        assert params.sort_dir == expected

    @pytest.mark.parametrize('_filter, expected', [
        pytest.param(None, None, id='None'),
        pytest.param("", None, id='empty string'),
        pytest.param("fake", 'fake', id='fake string'),
        pytest.param(0, '0', id='zero'),
        pytest.param(-1, '-1', id='negative'),
        pytest.param("0", '0', id='zero string'),
        pytest.param("-1", '-1', id='negative string'),
        pytest.param(5.5, '5.5', id='float'),
        pytest.param(True, 'True', id='True'),
        pytest.param(False, 'False', id='False'),
        pytest.param({}, '{}', id='dict'),
    ])
    def test_filter_prop(self, _filter: Any, expected: str | None):
        params = SearchParams(init_filter=_filter)  # type: ignore
        assert params.filter == expected


class TestSearchResult:

    def test_props_annotations(self):
        annotations = SearchResult.__annotations__
        assert annotations.keys() == {'items', 'total', 'current_page', 'per_page', 'last_page'}
        assert annotations['items'] == List[ET] # type: ignore
        assert annotations['total'] == int
        assert annotations['current_page'] == int
        assert annotations['per_page'] == int
        assert annotations['last_page'] == int
    
    def test_last_page_calculation(self):
        items = [1, 2, 3, 4, 5]
        total = 17
        current_page = 2
        per_page = 5
        search_result = SearchResult[int](
            items=items, total=total, current_page=current_page, per_page=per_page)
        assert search_result.last_page == 4

        items = [1, 2, 3, 4, 5]
        total = 15
        current_page = 3
        per_page = 5
        search_result = SearchResult[int](
            items=items, total=total, current_page=current_page, per_page=per_page)
        assert search_result.last_page == 3

        items = [1, 2, 3, 4, 5]
        total = 5
        current_page = 1
        per_page = 5
        search_result = SearchResult[int](
            items=items, total=total, current_page=current_page, per_page=per_page)
        assert search_result.last_page == 1

        items = [1, 2, 3, 4, 5]
        total = 0
        current_page = 1
        per_page = 5
        search_result = SearchResult[int](
            items=items, total=total, current_page=current_page, per_page=per_page)
        assert search_result.last_page == 0

        items = []
        total = 0
        current_page = 1
        per_page = 5
        search_result = SearchResult[int](
            items=items, total=total, current_page=current_page, per_page=per_page)
        assert search_result.last_page == 0
