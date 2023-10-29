import datetime
import pytest
from core.cast_member.domain.entities import CastMember, CastMemberId
from core.cast_member.domain.repositories import CastMemberFilter, ICastMemberRepository
from core.shared.domain.exceptions import NotFoundException
from django_app.cast_member_app.models import CastMemberDjangoRepository, CastMemberModel


@pytest.mark.django_db
class TestCastMemberDjangoRepository:

    repo: CastMemberDjangoRepository

    def setup_method(self):
        self.repo = CastMemberDjangoRepository()

    def test_insert(self):
        cast_member = CastMember.fake().a_director().build()

        self.repo.insert(cast_member)

        model = CastMemberModel.objects.get(pk=cast_member.cast_member_id.id)

        assert str(model.id) == cast_member.cast_member_id.id
        assert model.name == cast_member.name
        assert model.type == cast_member.type
        assert model.created_at == cast_member.created_at

        cast_member = CastMember(
            name='Movie 2',
            type=CastMember.ACTOR
        )

        self.repo.insert(cast_member)

        model = CastMemberModel.objects.get(pk=cast_member.entity_id.id)

        assert str(model.id) == cast_member.entity_id.id
        assert model.name == 'Movie 2'
        assert model.type == CastMember.ACTOR
        assert model.created_at == cast_member.created_at

    def test_bulk_insert(self):
        cast_members = CastMember.fake().the_cast_members(2)\
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=index))\
            .build()

        self.repo.bulk_insert(cast_members)

        models = CastMemberModel.objects.all()

        assert len(models) == 2
        assert str(models[0].id) == cast_members[1].cast_member_id.id
        assert models[0].name == cast_members[1].name
        assert models[0].type == cast_members[1].type
        assert models[0].created_at == cast_members[1].created_at

        assert str(models[1].id) == cast_members[0].cast_member_id.id
        assert models[1].name == cast_members[0].name
        assert models[1].type == cast_members[0].type
        assert models[1].created_at == cast_members[0].created_at

    def test_find_by_id(self):

        assert self.repo.find_by_id(CastMemberId()) is None

        cast_member = CastMember.fake().a_director().build()
        self.repo.insert(cast_member)

        cast_member_found = self.repo.find_by_id(cast_member.cast_member_id)
        assert cast_member_found == cast_member

    def test_find_all(self):
        cast_members = CastMember.fake().the_cast_members(2)\
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=index))\
            .build()
        self.repo.bulk_insert(cast_members)
        found_cast_members = self.repo.find_all()

        assert len(found_cast_members) == 2
        assert found_cast_members[0].cast_member_id == cast_members[1].cast_member_id
        assert found_cast_members[0].name == cast_members[1].name
        assert found_cast_members[0].type == cast_members[1].type
        assert found_cast_members[0].created_at == cast_members[1].created_at

        assert found_cast_members[1].cast_member_id == cast_members[0].cast_member_id
        assert found_cast_members[1].name == cast_members[0].name
        assert found_cast_members[1].type == cast_members[0].type
        assert found_cast_members[1].created_at == cast_members[0].created_at

    def test_throw_not_found_exception_in_update(self):
        cast_member = CastMember.fake().a_director().build()
        with pytest.raises(NotFoundException) as assert_error:
            self.repo.update(cast_member)
        assert assert_error.value.args[
            0] == f"CastMember with id {cast_member.cast_member_id.id} not found"

    def test_update(self):
        cast_member = CastMember.fake().a_director().build()
        self.repo.insert(cast_member)

        cast_member.change_name('Movie changed')
        cast_member.change_type(CastMember.ACTOR)

        self.repo.update(cast_member)

        model = CastMemberModel.objects.get(pk=cast_member.cast_member_id.id)

        assert str(model.id) == cast_member.cast_member_id.id
        assert model.name == cast_member.name
        assert model.type == cast_member.type
        assert model.created_at == cast_member.created_at

    def test_throw_not_found_exception_in_delete(self):
        cast_member_id = CastMemberId()
        with pytest.raises(NotFoundException) as assert_error:
            self.repo.delete(cast_member_id)
        assert assert_error.value.args[0] == f"CastMember with id {cast_member_id.id} not found"

    def test_delete(self):
        cast_member = CastMember.fake().a_director().build()
        self.repo.insert(cast_member)

        self.repo.delete(cast_member.cast_member_id)

        assert CastMemberModel.objects.filter(
            pk=cast_member.cast_member_id.id).count() == 0

    def test_search_when_params_is_empty(self):
        entities = CastMember.fake().the_cast_members(16).with_created_at(
            lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=index)
        ).build()
        self.repo.bulk_insert(entities)
        entities.reverse()

        search_result = self.repo.search(ICastMemberRepository.SearchParams())
        assert search_result == ICastMemberRepository.SearchResult(
            items=entities[:15],
            total=16,
            current_page=1,
            per_page=15,
        )

    def test_search_applying_paginate_and_filter_by_name(self):
        cast_members = [
            CastMember.fake().an_actor()
            .with_name('test')
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=4)
            )
            .build(),
            CastMember.fake().an_actor()
            .with_name('a')
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=3)
            )
            .build(),
            CastMember.fake().an_actor()
            .with_name('TEST')
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=2)
            )
            .build(),
            CastMember.fake().an_actor()
            .with_name('TeSt')
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=1)
            )
            .build(),
        ]
        self.repo.bulk_insert(cast_members)

        search_params = ICastMemberRepository.SearchParams(
            init_page=1,
            init_per_page=2,
            init_filter=CastMemberFilter(name='E')
        )
        search_result = self.repo.search(search_params)
        assert search_result == ICastMemberRepository.SearchResult(
            items=[
                cast_members[0],
                cast_members[2],
            ],
            total=3,
            current_page=1,
            per_page=2,
        )

    @pytest.mark.parametrize('search_params, expected_search_output', [
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_page=1,
                init_per_page=2,
                init_filter=CastMemberFilter(type=CastMember.ACTOR)
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    2, 1
                ],
                total=3,
                current_page=1,
                per_page=2,
            ),
            id='filter by type = actor, page = 1'
        ),
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_page=2,
                init_per_page=2,
                init_filter=CastMemberFilter(type=CastMember.ACTOR)
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    0
                ],
                total=3,
                current_page=2,
                per_page=2,
            ),
            id='filter by type = actor, page = 2'
        ),
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_page=1,
                init_per_page=2,
                init_filter=CastMemberFilter(type=CastMember.DIRECTOR)
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    5, 4
                ],
                total=3,
                current_page=1,
                per_page=2,
            ),
            id='filter by type = director, page = 1'
        ),
    ])
    def test_search_applying_paginate_and_filter_by_type(self,
                                                         search_params: ICastMemberRepository.SearchParams,
                                                         expected_search_output: ICastMemberRepository.SearchResult):
        cast_members = [
            CastMember.fake().an_actor()
            .with_name('actor1')
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=1)
            )
            .build(),
            CastMember.fake().an_actor()
            .with_name('actor2')
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=2)
            )
            .build(),
            CastMember.fake().an_actor()
            .with_name('actor3')
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=3)
            )
            .build(),
            CastMember.fake().a_director()
            .with_name('director1')
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=4)
            )
            .build(),
            CastMember.fake().a_director()
            .with_name('director2')
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=5)
            )
            .build(),
            CastMember.fake().a_director()
            .with_name('director3')
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=6)
            )
            .build(),
        ]
        self.repo.bulk_insert(cast_members)

        search_result = self.repo.search(search_params)
        expected_search_output.items = [cast_members[i]  # type: ignore
                                        for i in expected_search_output.items]
        assert search_result == expected_search_output

    @pytest.mark.parametrize('search_params, expected_search_output', [
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_per_page=2,
                init_sort='name'
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    1, 0
                ],
                total=5,
                current_page=1,
                per_page=2,
            ),
            id='sort by name asc, page = 1'
        ),
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_page=2,
                init_per_page=2,
                init_sort='name'
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    4, 2
                ],
                total=5,
                current_page=2,
                per_page=2,
            ),
            id='sort by name asc, page = 2'
        ),
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_per_page=2,
                init_sort='name',
                init_sort_dir='desc'
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    3, 2
                ],
                total=5,
                current_page=1,
                per_page=2,
            ),
            id='sort by name desc, page = 1'
        ),
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_page=2,
                init_per_page=2,
                init_sort='name',
                init_sort_dir='desc'
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    4, 0
                ],
                total=5,
                current_page=2,
                per_page=2,
            ),
            id='sort by name desc, page = 2'
        ),
    ])
    def test_search_applying_paginate_and_sort(self,
                                               search_params: ICastMemberRepository.SearchParams,
                                               expected_search_output: ICastMemberRepository.SearchResult):
        cast_members = [
            CastMember.fake().an_actor().with_name('b').build(),
            CastMember.fake().an_actor().with_name('a').build(),
            CastMember.fake().an_actor().with_name('d').build(),
            CastMember.fake().an_actor().with_name('e').build(),
            CastMember.fake().an_actor().with_name('c').build(),
        ]
        self.repo.bulk_insert(cast_members)

        search_result = self.repo.search(search_params)
        expected_search_output.items = [cast_members[i]  # type: ignore
                                        for i in expected_search_output.items]
        assert search_result == expected_search_output

    @pytest.mark.parametrize('search_params, expected_search_output', [
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_page=1,
                init_per_page=2,
                init_sort='name',
                init_filter=CastMemberFilter(name='TEST')
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    2, 4
                ],
                total=3,
                current_page=1,
                per_page=2,
            ),
            id='sort by name asc, filter by name = TEST page = 1'
        ),
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_page=2,
                init_per_page=2,
                init_filter=CastMemberFilter(name='TEST')
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    0
                ],
                total=3,
                current_page=2,
                per_page=2,
            ),
            id='sort by name asc, filter by name = TEST page = 2'
        ),
    ])
    def test_search_applying_sort_and_paginate_and_filter_by_name(self,
                                                                  search_params: ICastMemberRepository.SearchParams,
                                                                  expected_search_output: ICastMemberRepository.SearchResult):
        cast_members = [
            CastMember.fake().an_actor().with_name('test').build(),
            CastMember.fake().an_actor().with_name('a').build(),
            CastMember.fake().an_actor().with_name('TEST').build(),
            CastMember.fake().an_actor().with_name('e').build(),
            CastMember.fake().an_actor().with_name('TeSt').build(),
        ]
        self.repo.bulk_insert(cast_members)

        search_result = self.repo.search(search_params)
        expected_search_output.items = [cast_members[i]  # type: ignore
                                        for i in expected_search_output.items]
        assert search_result == expected_search_output

    @pytest.mark.parametrize('search_params, expected_search_output', [
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_page=1,
                init_per_page=2,
                init_sort='name',
                init_filter=CastMemberFilter(type=CastMember.ACTOR)
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    2, 4
                ],
                total=3,
                current_page=1,
                per_page=2,
            ),
            id='sort by name asc, filter by type = actor page = 1'
        ),
        pytest.param(
            ICastMemberRepository.SearchParams(

                init_page=2,
                init_per_page=2,
                init_filter=CastMemberFilter(type=CastMember.ACTOR)
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    0
                ],
                total=3,
                current_page=2,
                per_page=2,
            ),
            id='sort by name asc, filter by type = actor page = 2'
        ),
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_page=1,
                init_per_page=2,
                init_sort='name',
                init_filter=CastMemberFilter(type=CastMember.DIRECTOR)
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    1, 5
                ],
                total=3,
                current_page=1,
                per_page=2,
            ),
            id='sort by name asc, filter by type = director page = 1'
        ),
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_page=2,
                init_per_page=2,
                init_sort='name',
                init_filter=CastMemberFilter(type=CastMember.DIRECTOR)
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    3
                ],
                total=3,
                current_page=2,
                per_page=2,
            ),
            id='sort by name asc, filter by type = director page = 2'
        ),
    ])
    def test_search_applying_sort_and_paginate_and_filter_by_type(self,
                                                                  search_params: ICastMemberRepository.SearchParams,
                                                                  expected_search_output: ICastMemberRepository.SearchResult):
        cast_members = [
            CastMember.fake().an_actor().with_name('test').build(),
            CastMember.fake().a_director().with_name('a').build(),
            CastMember.fake().an_actor().with_name('TEST').build(),
            CastMember.fake().a_director().with_name('e').build(),
            CastMember.fake().an_actor().with_name('TeSt').build(),
            CastMember.fake().a_director().with_name('b').build(),
        ]
        self.repo.bulk_insert(cast_members)

        search_result = self.repo.search(search_params)
        expected_search_output.items = [cast_members[i]  # type: ignore
                                        for i in expected_search_output.items]
        assert search_result == expected_search_output

    @pytest.mark.parametrize('search_params, expected_search_output', [
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_page=1,
                init_per_page=2,
                init_sort='name',
                init_filter=CastMemberFilter(
                    name='TEST', type=CastMember.ACTOR)
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    2, 4
                ],
                total=3,
                current_page=1,
                per_page=2,
            ),
            id='sort by name asc, filter by name = TEST, type = actor page = 1'
        ),
        pytest.param(
            ICastMemberRepository.SearchParams(
                init_page=2,
                init_per_page=2,
                init_filter=CastMemberFilter(
                    name='TEST', type=CastMember.ACTOR)
            ),
            ICastMemberRepository.SearchResult(
                items=[
                    0
                ],
                total=3,
                current_page=2,
                per_page=2,
            ),
            id='sort by name asc, filter by name = TEST, type = actor page = 2'
        ),
    ])
    def test_search_applying_sort_and_paginate_and_filter_by_name_and_type(self,
                                                                           search_params: ICastMemberRepository.SearchParams,
                                                                           expected_search_output: ICastMemberRepository.SearchResult):
        cast_members = [
            CastMember.fake().an_actor().with_name('test').build(),
            CastMember.fake().a_director().with_name('a director').build(),
            CastMember.fake().an_actor().with_name('TEST').build(),
            CastMember.fake().a_director().with_name('e director').build(),
            CastMember.fake().an_actor().with_name('TeSt').build(),
            CastMember.fake().a_director().with_name('b director').build(),
        ]
        self.repo.bulk_insert(cast_members)

        search_result = self.repo.search(search_params)
        expected_search_output.items = [cast_members[i]  # type: ignore
                                        for i in expected_search_output.items]
        assert search_result == expected_search_output
