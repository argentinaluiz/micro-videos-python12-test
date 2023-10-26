from typing import List, Type
from core.cast_member.domain.entities import CastMember, CastMemberId, CastMemberType
from core.cast_member.domain.repositories import CastMemberFilter, ICastMemberRepository
from core.shared.domain.repositories import InMemorySearchableRepository
from core.shared.domain.search_params import SortDirection


class CastMemberInMemoryRepository(
        ICastMemberRepository,
        InMemorySearchableRepository[
            CastMember,
            CastMemberId, CastMemberFilter
        ]):
    sortable_fields: List[str] = ["name", "created_at"]

    def _apply_filter(self,
                      items: List[CastMember],
                      filter_param: CastMemberFilter | None = None) -> List[CastMember]:
        if filter_param:
            filter_obj = filter(
                lambda item: self._filter_logic(item, filter_param),
                items
            )
            return list(filter_obj)

        return items

    def _filter_logic(self, item: CastMember, filter_param: CastMemberFilter) -> bool:
        if filter_param.name and filter_param.type:
            return self._clause_name(item, filter_param.name) and \
                self._clause_type(item, filter_param.type)

        return self._clause_name(item, filter_param.name) \
            if filter_param.name \
            else self._clause_type(item, filter_param.type)

    def _clause_name(self, item: CastMember, name: str) -> bool:
        return name.lower() in item.name.lower()

    def _clause_type(self, item: CastMember, _type: CastMemberType) -> bool:
        return _type == item.type

    def _apply_sort(
        self,
        items: List[CastMember],
        sort: str | None = None,
        sort_dir: SortDirection | None = None,
    ) -> List[CastMember]:
        return super()._apply_sort(items, sort, sort_dir) \
            if sort \
            else super()._apply_sort(items, "created_at", SortDirection.DESC)

    def get_entity(self) -> Type[CastMember]:
        return CastMember
