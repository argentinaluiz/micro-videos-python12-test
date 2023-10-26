

from abc import ABC
from dataclasses import field
from core.shared.domain.repositories import ISearchableRepository
from core.shared.domain.search_params import (
    SearchParams as DefaultSearchParams,
    SearchResult as DefaultSearchResult
)
from core.cast_member.domain.entities import CastMember, CastMemberId, CastMemberType
from pydantic.dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CastMemberFilter:
    name: str | None = field(default=None)
    type: CastMemberType | None = field(default=None)


class _SearchParams(DefaultSearchParams[CastMemberFilter]):  # pylint: disable=too-few-public-methods
    pass


class _SearchResult(DefaultSearchResult[CastMember]):  # pylint: disable=too-few-public-methods
    pass


class ICastMemberRepository(ISearchableRepository[CastMember, CastMemberId], ABC):
    SearchParams = _SearchParams
    SearchResult = _SearchResult
