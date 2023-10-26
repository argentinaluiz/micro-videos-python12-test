import datetime
from typing import Tuple
from uuid import uuid4
from django_app.cast_member_app.models import CastMemberDjangoRepository

from core.cast_member.application.use_cases import CastMemberOutput, CreateCastMemberUseCase, DeleteCastMemberUseCase, GetCastMemberUseCase, ListCastMembersUseCase, UpdateCastMemberUseCase
from core.cast_member.domain.entities import CastMember, CastMemberId
from core.cast_member.domain.repositories import CastMemberFilter
import pytest
from _pytest.fixtures import SubRequest

from core.shared.domain.exceptions import NotFoundException


@pytest.mark.django_db
class TestCreateCastMemberUseCaseInt:

    use_case: CreateCastMemberUseCase
    cast_member_repo: CastMemberDjangoRepository

    def setup_method(self) -> None:
        self.cast_member_repo = CastMemberDjangoRepository()
        self.use_case = CreateCastMemberUseCase(self.cast_member_repo)

    def test_execute(self):
        input_param = CreateCastMemberUseCase.Input(
            name='director example', type=CastMember.DIRECTOR)
        output = self.use_case.execute(input_param)
        cast_member_created = self.cast_member_repo.find_by_id(
            CastMemberId(output.id))
        assert output == CreateCastMemberUseCase.Output(
            id=cast_member_created.cast_member_id.id,  # type: ignore
            name='director example',
            type=CastMember.DIRECTOR,
            created_at=cast_member_created.created_at  # type: ignore
        )

        input_param = CreateCastMemberUseCase.Input(
            name='actor example', type=CastMember.ACTOR)
        output = self.use_case.execute(input_param)
        cast_member_created = self.cast_member_repo.find_by_id(
            CastMemberId(output.id))
        assert output == CreateCastMemberUseCase.Output(
            id=cast_member_created.cast_member_id.id,  # type: ignore
            name='actor example',
            type=CastMember.ACTOR,
            created_at=cast_member_created.created_at  # type: ignore
        )


@pytest.mark.django_db
class TestGetCastMemberUseCaseInt:

    use_case: GetCastMemberUseCase
    cast_member_repo: CastMemberDjangoRepository

    def setup_method(self) -> None:
        self.cast_member_repo = CastMemberDjangoRepository()
        self.use_case = GetCastMemberUseCase(self.cast_member_repo)

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

    def test_execute(self):
        cast_member = CastMember.fake().a_director().build()
        self.cast_member_repo.insert(cast_member)
        input_param = GetCastMemberUseCase.Input(
            cast_member.cast_member_id.id)  # type: ignore
        output = self.use_case.execute(input_param)
        assert output == GetCastMemberUseCase.Output(
            id=cast_member.cast_member_id.id,
            name=cast_member.name,
            type=cast_member.type,
            created_at=cast_member.created_at
        )


@pytest.mark.django_db
class TestListCastMembersUseCaseInt:

    use_case: ListCastMembersUseCase
    cast_member_repo: CastMemberDjangoRepository

    def setup_method(self) -> None:
        self.cast_member_repo = CastMemberDjangoRepository()
        self.use_case = ListCastMembersUseCase(self.cast_member_repo)

    def test_execute_using_empty_search_params(self):
        items = [
            CastMember.fake().a_director().with_name('test 1').build(),
            CastMember.fake().a_director().with_name('test 2').with_created_at(
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=200)).build()
        ]
        self.cast_member_repo.bulk_insert(items)
        input_param = ListCastMembersUseCase.Input()
        output = self.use_case.execute(input_param)
        assert output == ListCastMembersUseCase.Output(
            items=list(
                map(CastMemberOutput.from_entity, items[::-1])
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
                    filter=CastMemberFilter(
                        name='director', type=CastMember.DIRECTOR)
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
                    filter=CastMemberFilter(
                        name='director', type=CastMember.DIRECTOR)
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


@pytest.mark.django_db
class TestUpdateCastMemberUseCaseInt:

    use_case: UpdateCastMemberUseCase
    cast_member_repo: CastMemberDjangoRepository

    def setup_method(self) -> None:
        self.cast_member_repo = CastMemberDjangoRepository()
        self.use_case = UpdateCastMemberUseCase(self.cast_member_repo)

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


@pytest.mark.django_db
class TestDeleteCastMemberUseCaseInt:

    use_case: DeleteCastMemberUseCase
    cast_member_repo: CastMemberDjangoRepository

    def setup_method(self) -> None:
        self.cast_member_repo = CastMemberDjangoRepository()
        self.use_case = DeleteCastMemberUseCase(self.cast_member_repo)

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
        self.cast_member_repo.insert(cast_member)
        request = DeleteCastMemberUseCase.Input(
            id=cast_member.cast_member_id.id)  # type: ignore
        self.use_case.execute(request)
        assert self.cast_member_repo.find_by_id(
            cast_member.cast_member_id) is None
