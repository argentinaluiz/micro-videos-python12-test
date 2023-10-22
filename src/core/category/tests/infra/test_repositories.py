import datetime
from core.category.domain.entities import Category
from core.category.infra.repositories import CategoryInMemoryRepository
from core.shared.domain.search_params import SortDirection


class TestCategoryInMemoryRepository:
    repo: CategoryInMemoryRepository

    def setup_method(self) -> None:
        self.repo = CategoryInMemoryRepository()

    def test_if_no_filter_when_filter_param_is_null(self):
        entity = Category.fake().a_category().build()
        items = [entity]

        items_filtered = self.repo._apply_filter(items, None) # pylint: disable=protected-access #type: ignore
        assert items_filtered == items

    def test_filter(self):
        items = [
            Category.fake().a_category().with_name('test').build(),
            Category.fake().a_category().with_name('TEST').build(),
            Category.fake().a_category().with_name('fake').build(),
        ]
        items_filtered = self.repo._apply_filter(items, 'TEST') # pylint: disable=protected-access #type: ignore
        assert items_filtered == [items[0], items[1]]

    def test_sort_by_created_at_when_sort_param_is_null(self):
        faker = Category.fake().a_category()
        items = [
            faker.with_name('test').build(),
            faker.with_name('TEST').with_created_at(
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
            ).build(),
            faker.with_name('fake').with_created_at(
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=2)
            ).build(),
        ]
        
        items_filtered = self.repo._apply_sort(items, None, None) # pylint: disable=protected-access #type: ignore
        assert items_filtered == [items[2], items[1], items[0]]

    def test_sort_by_name(self):
        items = [
            Category.fake().a_category().with_name('c').build(),
            Category.fake().a_category().with_name('b').build(),
            Category.fake().a_category().with_name('a').build(),
        ]

        items_filtered = self.repo._apply_sort(items, "name", SortDirection.ASC) # pylint: disable=protected-access #type: ignore
        assert items_filtered == [items[2], items[1], items[0]]

        items_filtered = self.repo._apply_sort(items, "name", SortDirection.DESC) # pylint: disable=protected-access #type: ignore
        assert items_filtered == [items[0], items[1], items[2]]
