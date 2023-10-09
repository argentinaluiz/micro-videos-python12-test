from abc import ABC
import abc
from dataclasses import dataclass as python_dataclass
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing import Any, Generic, List, TypeVar, TypedDict

from core.shared.domain.search_params import SearchResult, SortDirection


class UseCase(ABC):

    @abc.abstractmethod
    def execute(self, input_param: Any) -> Any:
        raise NotImplementedError()


Filter = TypeVar('Filter')


@pydantic_dataclass(slots=True, frozen=True)
class SearchInput(Generic[Filter]):
    page: int | None = None
    per_page: int | None = None
    sort: str | None = None
    sort_dir: SortDirection | None = None
    filter: Filter | None = None

    def to_repository_input(self):
        typed_dict = TypedDict('SearchParams', {
            'init_page': int | None,
            'init_per_page': int | None,
            'init_sort': str | None,
            'init_sort_dir': SortDirection | None,
            'init_filter': Filter | None
        })
        return typed_dict(
            init_page=self.page,
            init_per_page=self.per_page,
            init_sort=self.sort,
            init_sort_dir=self.sort_dir,
            init_filter=self.filter
        )


PaginationOutputItem = TypeVar('PaginationOutputItem')


@python_dataclass(frozen=True, slots=True)
class PaginationOutput(Generic[PaginationOutputItem]):
    items: List[PaginationOutputItem]
    total: int
    current_page: int
    per_page: int
    last_page: int

    @classmethod
    def from_search_result(cls,
                           result: SearchResult[Any],
                           items: List[PaginationOutputItem]):
        return cls(
            items=items,
            total=result.total,
            current_page=result.current_page,
            per_page=result.per_page,
            last_page=result.last_page
        )
