

from abc import ABC
from dataclasses import field
from typing import Set
from core.category.domain.entities import CategoryId
from core.category.domain.pydantic import CategoryIdAnnotated
from core.shared.domain.repositories import ISearchableRepository
from core.shared.domain.search_params import (
    SearchParams as DefaultSearchParams,
    SearchResult as DefaultSearchResult
)
from core.genre.domain.entities import Genre, GenreId
from pydantic.dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GenreFilter:
    name: str | None = field(default=None)
    categories_id: Set[CategoryIdAnnotated] | None = field(default=None)


class _SearchParams(DefaultSearchParams[GenreFilter]):  # pylint: disable=too-few-public-methods
    pass


class _SearchResult(DefaultSearchResult[Genre]):  # pylint: disable=too-few-public-methods
    pass


class IGenreRepository(ISearchableRepository[Genre, GenreId], ABC):
    SearchParams = _SearchParams
    SearchResult = _SearchResult
