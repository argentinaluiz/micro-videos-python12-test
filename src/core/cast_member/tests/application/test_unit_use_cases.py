from dataclasses import MISSING
import datetime
from typing import Optional, Tuple
from uuid import UUID, uuid4

from pydantic import StrictBool, ValidationError
from core.cast_member.application.use_cases import CastMemberOutput, CreateCastMemberUseCase, DeleteCastMemberUseCase, GetCastMemberUseCase, ListCastMembersUseCase, UpdateCastMemberUseCase
from core.cast_member.domain.entities import CastMember, CastMemberType
from core.cast_member.domain.repositories import CastMemberFilter, ICastMemberRepository
from core.cast_member.infra.repositories import CastMemberInMemoryRepository
from core.shared.application.use_cases import PaginationOutput, SearchInput, UseCase
from unittest.mock import patch
import pytest
from _pytest.fixtures import SubRequest

from core.shared.domain.exceptions import NotFoundException


class TestCastMemberOutputUnit:

    def test_fields(self):
        assert CastMemberOutput.__annotations__, {
            'id': str,
            'name': str,
            'type': CastMemberType,
            'created_at': datetime
        }

    def test_from_entity(self):
        cast_member = CastMember.fake().a_director().build()
        output = CastMemberOutput.from_entity(cast_member)
        assert output.id == cast_member.cast_member_id.id
        assert output.name == cast_member.name
        assert output.type == cast_member.type
        assert output.created_at == cast_member.created_at


class TestCreateCastMemberUseCaseUnit:

    use_case: CreateCastMemberUseCase
    cast_member_repo: CastMemberInMemoryRepository

    def setup_method(self) -> None:
        self.cast_member_repo = CastMemberInMemoryRepository()
        self.use_case = CreateCastMemberUseCase(self.cast_member_repo)

    def test_if_instance_a_use_case(self):
        assert isinstance(self.use_case, UseCase)

    def test_input_annotation(self):
        assert CreateCastMemberUseCase.Input.__annotations__, {
            'name': str,
            'type': CastMemberType,
        }

    def test_invalid_input(self):
        with pytest.raises(ValidationError) as assert_error:
            CreateCastMemberUseCase.Input()  # pylint: disable=no-value-for-parameter #type: ignore
        assert len(assert_error.value.errors()) == 2
        name_error = assert_error.value.errors()[0]
        assert 'name' in name_error['loc']
        assert 'missing' in name_error['type']
        assert 'Field required' == name_error['msg']

        type_error = assert_error.value.errors()[1]
        assert 'type' in type_error['loc']
        assert 'missing' in type_error['type']
        assert 'Field required' == type_error['msg']

        with pytest.raises(ValidationError) as assert_error:
            CreateCastMemberUseCase.Input(
                name=1, type='a')  # type: ignore
        assert len(assert_error.value.errors()) == 2

        name_error = assert_error.value.errors()[0]
        assert 'name' in name_error['loc']
        assert 'string_type' in name_error['type']
        assert 'Input should be a valid string' == name_error['msg']

        type_error = assert_error.value.errors()[1]
        assert 'type' in type_error['loc']
        assert 'literal_error' in type_error['type']
        assert 'Input should be 1 or 2' == type_error['msg']

    def test_output(self):
        assert issubclass(CreateCastMemberUseCase.Output, CastMemberOutput)

    def test_execute(self):

        with patch.object(
            self.cast_member_repo,
            'insert',
            wraps=self.cast_member_repo.insert
        ) as spy_insert:
            input_param = CreateCastMemberUseCase.Input(
                name='director example', type=CastMember.DIRECTOR)
            output = self.use_case.execute(input_param)
            spy_insert.assert_called_once()
            assert output == CreateCastMemberUseCase.Output(
                id=self.cast_member_repo.items[0].cast_member_id.id,
                name='director example',
                type=CastMember.DIRECTOR,
                created_at=self.cast_member_repo.items[0].created_at
            )

        input_param = CreateCastMemberUseCase.Input(
            name='actor example', type=CastMember.ACTOR)
        output = self.use_case.execute(input_param)
        assert output == CreateCastMemberUseCase.Output(
            id=self.cast_member_repo.items[1].cast_member_id.id,
            name='actor example',
            type=CastMember.ACTOR,
            created_at=self.cast_member_repo.items[1].created_at
        )


class TestGetCastMemberUseCaseUnit:

    use_case: GetCastMemberUseCase
    cast_member_repo: CastMemberInMemoryRepository

    def setup_method(self) -> None:
        self.cast_member_repo = CastMemberInMemoryRepository()
        self.use_case = GetCastMemberUseCase(self.cast_member_repo)

    def test_if_instance_a_use_case(self):
        assert issubclass(GetCastMemberUseCase, UseCase)

    def test_input(self):
        assert GetCastMemberUseCase.Input.__annotations__, {
            'id': UUID,
        }

    def test_invalid_input(self):
        with pytest.raises(ValidationError) as assert_error:
            GetCastMemberUseCase.Input('invalid_id')  # type: ignore
        assert 'Input should be a valid UUID' in assert_error.value.errors()[
            0]['msg']

    def test_throws_exception_when_cast_member_not_found(self):
        input_param = GetCastMemberUseCase.Input(
            '5f4b87a0-7b4a-4c1d-8e0a-0e8a0e9f1b9a')  # type: ignore
        with pytest.raises(NotFoundException) as assert_error:
            self.use_case.execute(input_param)
        assert assert_error.value.args[0] == "CastMember with id 5f4b87a0-7b4a-4c1d-8e0a-0e8a0e9f1b9a not found"

        input_param = GetCastMemberUseCase.Input(uuid4())
        with pytest.raises(NotFoundException) as assert_error:
            self.use_case.execute(input_param)
        assert assert_error.value.args[0] == f"CastMember with id {input_param.id} not found"

    def test_output(self):
        assert issubclass(GetCastMemberUseCase.Output, CastMemberOutput)

    def test_execute(self):
        cast_member = CastMember.fake().a_director().build()
        self.cast_member_repo.items = [cast_member]
        with patch.object(
            self.cast_member_repo,
            'find_by_id',
            wraps=self.cast_member_repo.find_by_id
        ) as spy_find_by_id:
            input_param = GetCastMemberUseCase.Input(
                cast_member.cast_member_id.id)  # type: ignore
            output = self.use_case.execute(input_param)
            spy_find_by_id.assert_called_once()
            assert output == GetCastMemberUseCase.Output(
                id=cast_member.cast_member_id.id,
                name=cast_member.name,
                type=cast_member.type,
                created_at=cast_member.created_at
            )


class TestListCastMembersUseCaseUnit:

    use_case: ListCastMembersUseCase
    cast_member_repo: CastMemberInMemoryRepository

    def setup_method(self) -> None:
        self.cast_member_repo = CastMemberInMemoryRepository()
        self.use_case = ListCastMembersUseCase(self.cast_member_repo)

    def test_instance_use_case(self):
        assert issubclass(ListCastMembersUseCase, UseCase)

    def test_input(self):
        assert issubclass(ListCastMembersUseCase.Input, SearchInput)

    def test_output(self):
        assert issubclass(ListCastMembersUseCase.Output, PaginationOutput)

    def test__to_output(self):

        default_props = {
            'total': 1,
            'current_page': 1,
            'per_page': 2,
        }

        result = ICastMemberRepository.SearchResult(items=[], **default_props)
        output = self.use_case._ListCastMembersUseCase__to_output(   # pylint: disable=protected-access #type: ignore
            result
        )
        assert output == ListCastMembersUseCase.Output(
            items=[],
            total=1,
            current_page=1,
            per_page=2,
            last_page=1,
        )

        entity = CastMember.fake().a_director().build()
        result = ICastMemberRepository.SearchResult(
            items=[entity], **default_props)
        output = self.use_case._ListCastMembersUseCase__to_output(  # pylint: disable=protected-access #type: ignore
            result)
        assert output == ListCastMembersUseCase.Output(
            items=[CastMemberOutput.from_entity(entity)],
            total=1,
            current_page=1,
            per_page=2,
            last_page=1,
        )

    def test_execute_using_empty_search_params(self):
        items = [
            CastMember.fake().a_director().with_name('test 1').build(),
            CastMember.fake().a_director().with_name('test 2').with_created_at(
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=200)).build()
        ]
        self.cast_member_repo.bulk_insert(items)
        with patch.object(
            self.cast_member_repo,
            'search',
            wraps=self.cast_member_repo.search
        ) as spy_search:
            input_param = ListCastMembersUseCase.Input()
            output = self.use_case.execute(input_param)
            spy_search.assert_called_once()
            assert output == ListCastMembersUseCase.Output(
                items=list(
                    map(CastMemberOutput.from_entity,
                        self.cast_member_repo.items[::-1])
                ),
                total=2,
                current_page=1,
                per_page=15,
                last_page=1
            )

    @pytest.mark.parametrize(
        'input_param, expected_output',
        (
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=1,
                    per_page=2,
                    filter=CastMemberFilter(name='TEST')
                ),
                ListCastMembersUseCase.Output(
                    items=[3, 2],
                    total=3,
                    current_page=1,
                    per_page=2,
                    last_page=2
                ),
                id='filter by name = TEST, page = 1, per_page = 2'
            ),
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=2,
                    per_page=2,
                    filter=CastMemberFilter(name='TEST')
                ),
                ListCastMembersUseCase.Output(
                    items=[0],
                    total=3,
                    current_page=2,
                    per_page=2,
                    last_page=2
                ),
                id='filter by name = TEST, page = 2, per_page = 2'
            ),
        ),
    )
    def test_execute_using_pagination_and_filter_by_name(self, input_param, expected_output):
        items = [
            CastMember.fake()
            .an_actor()
            .with_name("test")
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=1))
            .build(),
            CastMember.fake()
            .an_actor()
            .with_name("a")
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=2))
            .build(),
            CastMember.fake()
            .an_actor()
            .with_name("TEST")
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=3))
            .build(),
            CastMember.fake()
            .an_actor()
            .with_name("TeSt")
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=4))
            .build(),
        ]
        self.cast_member_repo.bulk_insert(items)
        output = self.use_case.execute(input_param)
        object.__setattr__(expected_output, 'items', [CastMemberOutput.from_entity(items[i])  # type: ignore
                                                      for i in expected_output.items])
        assert output == expected_output

    @pytest.mark.parametrize(
        'input_param, expected_output',
        (
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=1,
                    per_page=2,
                    filter=CastMemberFilter(type=CastMember.ACTOR)
                ),
                ListCastMembersUseCase.Output(
                    items=[2, 1],
                    total=3,
                    current_page=1,
                    per_page=2,
                    last_page=2
                ),
                id='filter by type = ACTOR, page = 1, per_page = 2'
            ),
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=2,
                    per_page=2,
                    filter=CastMemberFilter(type=CastMember.ACTOR)
                ),
                ListCastMembersUseCase.Output(
                    items=[0],
                    total=3,
                    current_page=2,
                    per_page=2,
                    last_page=2
                ),
                id='filter by type = ACTOR, page = 2, per_page = 2'
            ),
        ),
    )
    def test_execute_using_pagination_and_filter_by_type(self, input_param, expected_output):
        items = [
            CastMember.fake()
            .an_actor()
            .with_name("actor1")
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=1))
            .build(),
            CastMember.fake()
            .an_actor()
            .with_name("actor2")
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=2))
            .build(),
            CastMember.fake()
            .an_actor()
            .with_name("actor3")
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=3))
            .build(),
            CastMember.fake()
            .a_director()
            .with_name("director1")
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=4))
            .build(),
            CastMember.fake()
            .a_director()
            .with_name("director2")
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=5))
            .build(),
            CastMember.fake()
            .a_director()
            .with_name("director3")
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=6))
            .build(),
        ]
        self.cast_member_repo.bulk_insert(items)
        output = self.use_case.execute(input_param)
        object.__setattr__(expected_output, 'items', [CastMemberOutput.from_entity(items[i])  # type: ignore
                                                      for i in expected_output.items])
        assert output == expected_output

    @pytest.mark.parametrize(
        'input_param, expected_output',
        (
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=1,
                    per_page=2,
                    sort='name'
                ),
                ListCastMembersUseCase.Output(
                    items=[1, 0],
                    total=5,
                    current_page=1,
                    per_page=2,
                    last_page=3
                ),
                id='sort by name asc, page = 1, per_page = 2'
            ),
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=2,
                    per_page=2,
                    sort='name'
                ),
                ListCastMembersUseCase.Output(
                    items=[4, 2],
                    total=5,
                    current_page=2,
                    per_page=2,
                    last_page=3
                ),
                id='sort by name asc, page = 2, per_page = 2'
            ),
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=1,
                    per_page=2,
                    sort='name',
                    sort_dir='desc'
                ),
                ListCastMembersUseCase.Output(
                    items=[3, 2],
                    total=5,
                    current_page=1,
                    per_page=2,
                    last_page=3
                ),
                id='sort by name asc, page = 1, per_page = 2'
            ),
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=2,
                    per_page=2,
                    sort='name',
                    sort_dir='desc'
                ),
                ListCastMembersUseCase.Output(
                    items=[4, 0],
                    total=5,
                    current_page=2,
                    per_page=2,
                    last_page=3
                ),
                id='sort by name asc, page = 2, per_page = 2'
            ),
        )
    )
    def test_execute_using_pagination_and_sort_and_filter(self,
                                                          input_param: ListCastMembersUseCase.Input,
                                                          expected_output: ListCastMembersUseCase.Output):
        items = [
            CastMember.fake().an_actor().with_name("b").build(),
            CastMember.fake().an_actor().with_name("a").build(),
            CastMember.fake().an_actor().with_name("d").build(),
            CastMember.fake().an_actor().with_name("e").build(),
            CastMember.fake().an_actor().with_name("c").build(),
        ]
        self.cast_member_repo.bulk_insert(items)

        output = self.use_case.execute(input_param)
        object.__setattr__(expected_output, 'items', [CastMemberOutput.from_entity(items[i])  # type: ignore
                                                      for i in expected_output.items])
        assert output == expected_output

    @pytest.mark.parametrize(
        'input_param, expected_output',
        (
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=1,
                    per_page=2,
                    sort='name',
                    filter=CastMemberFilter(name='TEST')
                ),
                ListCastMembersUseCase.Output(
                    items=[2, 4],
                    total=3,
                    current_page=1,
                    per_page=2,
                    last_page=2
                ),
                id='sort by name asc, filter by name = TEST, page = 1, per_page = 2'
            ),
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=2,
                    per_page=2,
                    sort='name',
                    filter=CastMemberFilter(name='TEST')
                ),
                ListCastMembersUseCase.Output(
                    items=[0],
                    total=3,
                    current_page=2,
                    per_page=2,
                    last_page=2
                ),
                id='sort by name asc, filter by name = TEST, page = 2, per_page = 2'
            ),
        )
    )    
    def test_execute_using_pagination_and_sort_and_filter_by_name(self,
                                                                  input_param: ListCastMembersUseCase.Input,
                                                                  expected_output: ListCastMembersUseCase.Output):
        items = [
            CastMember.fake().an_actor().with_name("test").build(),
            CastMember.fake().an_actor().with_name("a").build(),
            CastMember.fake().an_actor().with_name("TEST").build(),
            CastMember.fake().an_actor().with_name("e").build(),
            CastMember.fake().a_director().with_name("TeSt").build(),
        ]
        self.cast_member_repo.bulk_insert(items)
        output = self.use_case.execute(input_param)
        object.__setattr__(expected_output, 'items', [CastMemberOutput.from_entity(items[i])  # type: ignore
                                                      for i in expected_output.items])
        assert output == expected_output

    @pytest.mark.parametrize(
        'input_param, expected_output',
        (
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=1,
                    per_page=2,
                    sort='name',
                    filter=CastMemberFilter(type=CastMember.ACTOR)
                ),
                ListCastMembersUseCase.Output(
                    items=[2, 4],
                    total=3,
                    current_page=1,
                    per_page=2,
                    last_page=2
                ),
                id='sort by name asc, filter by type = ACTOR, page = 1, per_page = 2'
            ),
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=2,
                    per_page=2,
                    sort='name',
                    filter=CastMemberFilter(type=CastMember.ACTOR)
                ),
                ListCastMembersUseCase.Output(
                    items=[0],
                    total=3,
                    current_page=2,
                    per_page=2,
                    last_page=2
                ),
                id='sort by name asc, filter by type = ACTOR, page = 2, per_page = 2'
            ),
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=1,
                    per_page=2,
                    sort='name',
                    filter=CastMemberFilter(type=CastMember.DIRECTOR)
                ),
                ListCastMembersUseCase.Output(
                    items=[1, 5],
                    total=3,
                    current_page=1,
                    per_page=2,
                    last_page=2
                ),
                id='sort by name asc, filter by type = DIRECTOR, page = 1, per_page = 2'
            ),
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=2,
                    per_page=2,
                    sort='name',
                    filter=CastMemberFilter(type=CastMember.DIRECTOR)
                ),
                ListCastMembersUseCase.Output(
                    items=[3],
                    total=3,
                    current_page=2,
                    per_page=2,
                    last_page=2
                ),
                id='sort by name asc, filter by type = DIRECTOR, page = 2, per_page = 2'
            ),
        )
    )    
    def test_execute_using_pagination_and_sort_and_filter_by_type(self,
                                                                  input_param: ListCastMembersUseCase.Input,
                                                                  expected_output: ListCastMembersUseCase.Output):
        items = [
            CastMember.fake().an_actor().with_name("test").build(),
            CastMember.fake().a_director().with_name("a").build(),
            CastMember.fake().an_actor().with_name("TEST").build(),
            CastMember.fake().a_director().with_name("e").build(),
            CastMember.fake().an_actor().with_name("TeSt").build(),
            CastMember.fake().a_director().with_name("b").build(),
        ]
        self.cast_member_repo.bulk_insert(items)
        output = self.use_case.execute(input_param)
        object.__setattr__(expected_output, 'items', [CastMemberOutput.from_entity(items[i])  # type: ignore
                                                      for i in expected_output.items])
        assert output == expected_output
    

    @pytest.mark.parametrize(
        'input_param, expected_output',
        (
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=1,
                    per_page=2,
                    sort='name',
                    filter=CastMemberFilter(name='TEST', type=CastMember.ACTOR)
                ),
                ListCastMembersUseCase.Output(
                    items=[2, 4],
                    total=3,
                    current_page=1,
                    per_page=2,
                    last_page=2
                ),
                id='sort by name asc, filter by name = TEST, type = ACTOR, page = 1, per_page = 2'
            ),
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=2,
                    per_page=2,
                    sort='name',
                    filter=CastMemberFilter(name='TEST', type=CastMember.ACTOR)
                ),
                ListCastMembersUseCase.Output(
                    items=[0],
                    total=3,
                    current_page=2,
                    per_page=2,
                    last_page=2
                ),
                id='sort by name asc, filter by name = TEST, type = ACTOR, page = 2, per_page = 2'
            ),
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=1,
                    per_page=2,
                    sort='name',
                    filter=CastMemberFilter(name='director', type=CastMember.DIRECTOR)
                ),
                ListCastMembersUseCase.Output(
                    items=[1, 5],
                    total=3,
                    current_page=1,
                    per_page=2,
                    last_page=2
                ),
                id='sort by name asc, filter by name = director, type = DIRECTOR, page = 1, per_page = 2'
            ),
            pytest.param(
                ListCastMembersUseCase.Input(
                    page=2,
                    per_page=2,
                    sort='name',
                    filter=CastMemberFilter(name='director', type=CastMember.DIRECTOR)
                ),
                ListCastMembersUseCase.Output(
                    items=[3],
                    total=3,
                    current_page=2,
                    per_page=2,
                    last_page=2
                ),
                id='sort by name asc, filter by name = director, type = DIRECTOR, page = 2, per_page = 2'
            ),
        )
    )    
    def test_execute_using_pagination_and_sort_and_filter_by_name_and_type(self,
                                                                  input_param: ListCastMembersUseCase.Input,
                                                                  expected_output: ListCastMembersUseCase.Output):
        items = [
            CastMember.fake().an_actor().with_name("test").build(),
            CastMember.fake().a_director().with_name("a director").build(),
            CastMember.fake().an_actor().with_name("TEST").build(),
            CastMember.fake().a_director().with_name("e director").build(),
            CastMember.fake().an_actor().with_name("TeSt").build(),
            CastMember.fake().a_director().with_name("b director").build(),
        ]
        self.cast_member_repo.bulk_insert(items)
        output = self.use_case.execute(input_param)
        object.__setattr__(expected_output, 'items', [CastMemberOutput.from_entity(items[i])  # type: ignore
                                                      for i in expected_output.items])
        assert output == expected_output


class TestUpdateCastMemberUseCaseUnit:

    use_case: UpdateCastMemberUseCase
    cast_member_repo: CastMemberInMemoryRepository

    def setup_method(self) -> None:
        self.cast_member_repo = CastMemberInMemoryRepository()
        self.use_case = UpdateCastMemberUseCase(self.cast_member_repo)

    def test_instance_use_case(self):
        assert isinstance(self.use_case, UseCase)

    def test_invalid_input(self):
        with pytest.raises(ValidationError) as assert_error:
            UpdateCastMemberUseCase.Input()  # pylint: disable=no-value-for-parameter #type: ignore
        assert len(assert_error.value.errors()) == 1
        assert 'id' in assert_error.value.errors()[0]['loc']
        assert 'missing' in assert_error.value.errors()[0]['type']
        assert 'Field required' in assert_error.value.errors()[
            0]['msg']

        with pytest.raises(ValidationError) as assert_error:
            UpdateCastMemberUseCase.Input(
                id=1, name=1, type='a')  # type: ignore
        assert len(assert_error.value.errors()) == 3

        uuid_error = assert_error.value.errors()[0]
        assert 'id' in uuid_error['loc']
        assert 'uuid_type' in uuid_error['type']
        assert 'UUID input should be a string, bytes or UUID object' in uuid_error['msg']

        name_error = assert_error.value.errors()[1]
        assert 'name' in name_error['loc']
        assert 'string_type' in name_error['type']
        assert 'Input should be a valid string' in name_error['msg']

        type_error = assert_error.value.errors()[2]
        assert 'type' in type_error['loc']
        assert 'literal_error' in type_error['type']
        assert 'Input should be 1 or 2' in type_error['msg']

    def test_input(self):
        assert UpdateCastMemberUseCase.Input.__annotations__, {
            'id': UUID,
            'name': Optional[str],
            'type': Optional[CastMemberType],
        }

        # # pylint: disable=no-member
        type_field = UpdateCastMemberUseCase.Input.__dataclass_fields__[
            'type']
        assert type_field.default is None

    def test_output(self):
        assert issubclass(UpdateCastMemberUseCase.Output, CastMemberOutput)

    def test_throw_exception_when_cast_member_not_found(self):
        _id = uuid4()
        request = UpdateCastMemberUseCase.Input(id=_id)
        with pytest.raises(NotFoundException) as assert_error:
            self.use_case.execute(request)
        assert assert_error.value.args[0] == f"CastMember with id {str(_id)} not found"

    # Defina a fixture dentro da classe
    @ pytest.fixture
    def execute_fixture(self, request: SubRequest):
        entity = request.param['entity']
        self.cast_member_repo.insert(entity)

        input_param = UpdateCastMemberUseCase.Input(
            id=entity.cast_member_id.id,  # type: ignore
            **request.param['input']
        )

        output_dict = {
            'id': entity.cast_member_id.id,  # type: ignore
            'name': entity.name,
            'type': entity.type,
            'created_at': entity.created_at
        }

        output_dict |= request.param['expected_output']

        output = UpdateCastMemberUseCase.Output(**output_dict)

        yield (input_param, output)

    @ pytest.mark.parametrize(
        'execute_fixture',
        (
            pytest.param({
                'entity': CastMember.fake().a_director().build(),
                'input': {},
                'expected_output': {}
            }, id='empty'),
            pytest.param({
                'entity': CastMember.fake().a_director().build(),
                'input': {
                    'name': 'test 2',
                    'type': CastMember.ACTOR,
                },
                'expected_output': {
                    'name': 'test 2',
                    'type': CastMember.ACTOR,
                }
            }, id='name and description'),
            pytest.param({
                'entity': CastMember.fake().a_director().build(),
                'input': {
                    'name': 'test',
                },
                'expected_output': {
                    'name': 'test',
                }
            }, id='only name'),
            pytest.param({
                'entity': CastMember.fake().an_actor().build(),
                'input': {
                    'type': CastMember.DIRECTOR,
                },
                'expected_output': {
                    'type': CastMember.DIRECTOR,
                }
            }, id='only is_active')
        ),
        indirect=True
    )
    def test_execute(self, execute_fixture: Tuple[UpdateCastMemberUseCase.Input, UpdateCastMemberUseCase.Output]):
        input_param, expected_output = execute_fixture
        output = self.use_case.execute(input_param)
        assert output == expected_output


class TestDeleteCastMemberUseCaseUnit:

    use_case: DeleteCastMemberUseCase
    cast_member_repo: CastMemberInMemoryRepository

    def setup_method(self) -> None:
        self.cast_member_repo = CastMemberInMemoryRepository()
        self.use_case = DeleteCastMemberUseCase(self.cast_member_repo)

    def test_instance_use_case(self):
        assert issubclass(DeleteCastMemberUseCase, UseCase)

    def test_input(self):
        assert DeleteCastMemberUseCase.Input.__annotations__, {
            'id': UUID,
        }

    def test_invalid_input(self):
        with pytest.raises(ValidationError) as assert_error:
            DeleteCastMemberUseCase.Input('invalid_id')  # type: ignore
        assert 'Input should be a valid UUID' in assert_error.value.errors()[
            0]['msg']

    def test_throws_exception_when_cast_member_not_found(self):
        input_param = DeleteCastMemberUseCase.Input(
            '5f4b87a0-7b4a-4c1d-8e0a-0e8a0e9f1b9a')  # type: ignore
        with pytest.raises(NotFoundException) as assert_error:
            self.use_case.execute(input_param)
        assert assert_error.value.args[0] == "CastMember with id 5f4b87a0-7b4a-4c1d-8e0a-0e8a0e9f1b9a not found"

        input_param = DeleteCastMemberUseCase.Input(uuid4())
        with pytest.raises(NotFoundException) as assert_error:
            self.use_case.execute(input_param)
        assert assert_error.value.args[0] == f"CastMember with id {input_param.id} not found"

    def test_execute(self):
        cast_member = CastMember.fake().a_director().build()
        self.cast_member_repo.items = [cast_member]
        with patch.object(
            self.cast_member_repo,
            'delete',
            wraps=self.cast_member_repo.delete
        ) as spy_delete:
            request = DeleteCastMemberUseCase.Input(
                id=cast_member.cast_member_id.id)  # type: ignore
            self.use_case.execute(request)
            spy_delete.assert_called_once()
            assert len(self.cast_member_repo.items) == 0
