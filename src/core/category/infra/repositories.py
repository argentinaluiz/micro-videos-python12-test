from typing import List, Type
from core.category.domain.entities import Category
from core.category.domain.repositories import ICategoryRepository
from core.shared.domain.repositories import InMemorySearchableRepository
from core.shared.domain.search_params import SortDirection
from core.shared.domain.value_objects import Uuid


class CategoryInMemoryRepository(
        ICategoryRepository,
        InMemorySearchableRepository[
            Category,
            Uuid, str
        ]):
    sortable_fields: List[str] = ["name", "created_at"]

    def _apply_filter(self,
                      items: List[Category],
                      filter_param: str | None = None) -> List[Category]:
        if filter_param:
            filter_obj = filter(
                lambda i: filter_param.lower() in i.name.lower(),
                items
            )
            return list(filter_obj)

        return items

    def _apply_sort(
        self,
        items: List[Category],
        sort: str | None = None,
        sort_dir: SortDirection | None = None,
    ) -> List[Category]:
        return super()._apply_sort(items, sort, sort_dir) \
            if sort \
            else super()._apply_sort(items, "created_at", SortDirection.DESC)

    def get_entity(self) -> Type[Category]:
        return Category

# validação
# repositório - ordenação - created_at, filter - name
