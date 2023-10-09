

from abc import ABC
from core.shared.domain.repositories import ISearchableRepository
from core.shared.domain.search_params import (
    SearchParams as DefaultSearchParams,
    SearchResult as DefaultSearchResult
)
from core.category.domain.entities import Category
from core.shared.domain.value_objects import Uuid


class _SearchParams(DefaultSearchParams[str]):  # pylint: disable=too-few-public-methods
    pass


class _SearchResult(DefaultSearchResult[Category]):  # pylint: disable=too-few-public-methods
    pass


class ICategoryRepository(ISearchableRepository[Category, Uuid], ABC):
    SearchParams = _SearchParams
    SearchResult = _SearchResult
