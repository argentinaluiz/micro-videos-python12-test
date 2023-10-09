from dataclasses import Field, InitVar, dataclass, field
from enum import Enum
import math
from typing import Any, Generic, List, Literal, TypeVar, cast

class SortDirection(Enum):
    ASC = 'asc'
    DESC = 'desc'

    def equals(self, value: Any):
        return value == self.value


SortDirectionValues = Literal['asc', 'desc']

Filter = TypeVar('Filter', str, Any)

# usar frozen causa um bug
@dataclass(slots=True, kw_only=True)
class SearchParams(Generic[Filter]):
    page: int = field(init=False, default=1)
    per_page: int = field(init=False, default=15)
    sort: str | None = field(init=False, default=None)
    sort_dir: SortDirection | None = field(init=False, default=None)
    filter: Filter | None = field(init=False, default=None)

    init_page: InitVar[int | None] = None
    init_per_page: InitVar[int | None] = None
    init_sort: InitVar[str | None] = None
    init_sort_dir: InitVar[SortDirectionValues | SortDirection | None] = None
    init_filter: InitVar[Filter | None] = None

    # pylint: disable=too-many-arguments
    def __post_init__(self, init_page: int | None,
                      init_per_page: int | None,
                      init_sort: str | None,
                      init_sort_dir: SortDirectionValues | SortDirection | None,
                      init_filter: Filter | None):
        self._normalize_page(init_page)
        self._normalize_per_page(init_per_page)
        self._normalize_sort(init_sort)
        self._normalize_sort_dir(init_sort_dir)
        self._normalize_filter(init_filter)

    def _normalize_page(self, page: int | None):
        page = _int_or_none(page)
        if page <= 0:
            page = cast(int, self.get_field('page').default)
        self.page = page

    def _normalize_per_page(self, per_page: int | None):
        per_page = _int_or_none(per_page)
        if per_page < 1:
            per_page = cast(int, self.get_field('per_page').default)
        self.per_page = per_page

    def _normalize_sort(self, sort: str | None):
        sort = None if sort == "" or sort is None else str(sort)
        self.sort = sort

    def _normalize_sort_dir(self, sort_dir: SortDirectionValues | SortDirection | None):
        if not self.sort:
            self.sort_dir = None
            return

        if isinstance(sort_dir, SortDirection):
            self.sort_dir = sort_dir
            return

        sort_dir = str(sort_dir).lower()  # type: ignore
        sort_dir = SortDirection.DESC if sort_dir == 'desc' else SortDirection.ASC
        self.sort_dir = sort_dir

    def _normalize_filter(self, _filter: Filter | None):
        _filter = None if _filter is None or _filter == "" else cast(
            Filter, str(_filter))
        self.filter = _filter

    @classmethod
    def get_field(cls, entity_field: str) -> Field[Any]:
        # pylint: disable=no-member
        return cls.__dataclass_fields__[entity_field]


def _int_or_none(value: Any, default: int = 0) -> int:
    try:
        return value if isinstance(value, int) else int(value)
    except (ValueError, TypeError):
        return default


SearchResultItem = TypeVar('SearchResultItem', bound=Any)

# usar frozen causa um bug
@dataclass(slots=True, kw_only=True)
class SearchResult(Generic[SearchResultItem]):
    items: List[SearchResultItem]
    total: int
    current_page: int
    per_page: int
    last_page: int = field(init=False)

    def __post_init__(self):
        object.__setattr__(
            self,
            'last_page',
            math.ceil(self.total / self.per_page)
        )
