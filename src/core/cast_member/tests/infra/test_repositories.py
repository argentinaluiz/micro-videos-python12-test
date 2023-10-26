# pylint: disable=unexpected-keyword-arg
import datetime
from core.cast_member.domain.entities import CastMember
from core.cast_member.domain.repositories import CastMemberFilter

from core.cast_member.infra.repositories import CastMemberInMemoryRepository
from core.shared.domain.search_params import SortDirection


class TestCastMemberInMemoryRepository:
    repo: CastMemberInMemoryRepository

    def setup_method(self) -> None:
        self.repo = CastMemberInMemoryRepository()

    def test_if_no_filter_when_filter_param_is_null(self):
        entity = CastMember.fake().an_actor().build()
        items = [entity]

        # pylint: disable=protected-access
        items_filtered = self.repo._apply_filter(
            items, None)
        assert items_filtered == items

    def test_filter_by_name(self):
        faker = CastMember.fake().an_actor()
        items = [
            faker.with_name('test').build(),
            faker.with_name('TEST').build(),
            faker.with_name('fake').build(),
        ]
        _filter = CastMemberFilter(name='TEST')
        # pylint: disable=protected-access
        items_filtered = self.repo._apply_filter(
            items, _filter)
        assert items_filtered == [items[0], items[1]]

    def test_filter_by_type(self):
        faker = CastMember.fake().an_actor()
        items = [
            faker.with_type(CastMember.ACTOR).build(),
            faker.with_type(CastMember.DIRECTOR).build(),
            faker.with_type(CastMember.ACTOR).build(),
        ]
        _filter = CastMemberFilter(type=items[0].type)
        # pylint: disable=protected-access
        items_filtered = self.repo._apply_filter(
            items, _filter)
        assert items_filtered == [items[0], items[2]]

    def test_filter_by_name_and_type(self):
        faker = CastMember.fake().an_actor()
        items = [
            faker.with_name('test').with_type(CastMember.ACTOR).build(),
            faker.with_name('TEST').with_type(CastMember.DIRECTOR).build(),
            faker.with_name('fake').with_type(CastMember.ACTOR).build(),
        ]
        _filter = CastMemberFilter(name='TEST', type=items[1].type)
        # pylint: disable=protected-access
        items_filtered = self.repo._apply_filter(
            items, _filter)
        assert items_filtered == [items[1]]

    def test_sort_by_created_at_when_sort_param_is_null(self):
        faker = CastMember.fake().an_actor()
        items = [
            faker.build(),
            faker.with_created_at(
                lambda self, index: datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(seconds=100)
            ).build(),
            faker.with_created_at(
                lambda self, index: datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(seconds=200)
            ).build(),
        ]
        # pylint: disable=protected-access
        items_filtered = self.repo._apply_sort(items, None, None)
        assert items_filtered == [items[2], items[1], items[0]]

    def test_sort_by_name(self):
        faker = CastMember.fake().an_actor()
        items = [
            faker.with_name('c').build(),
            faker.with_name('b').build(),
            faker.with_name('a').build(),
        ]

        # pylint: disable=protected-access
        items_filtered = self.repo._apply_sort(
            items, "name", SortDirection.ASC)
        assert items_filtered == [items[2], items[1], items[0]]

        # pylint: disable=protected-access
        items_filtered = self.repo._apply_sort(
            items, "name", SortDirection.DESC)
        assert items_filtered == [items[0], items[1], items[2]]
