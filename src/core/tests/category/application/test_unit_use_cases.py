from dataclasses import MISSING
import datetime
from typing import Optional, Tuple
from uuid import UUID, uuid4

from pydantic import StrictBool, ValidationError
from core.category.application.use_cases import CategoryOutput, CreateCategoryUseCase, DeleteCategoryUseCase, GetCategoryUseCase, ListCategoriesUseCase, UpdateCategoryUseCase
from core.category.domain.entities import Category
from core.category.domain.repositories import ICategoryRepository
from core.category.infra.repositories import CategoryInMemoryRepository
from core.shared.application.use_cases import PaginationOutput, SearchInput, UseCase
from unittest.mock import patch
import pytest
from _pytest.fixtures import SubRequest

from core.shared.domain.exceptions import NotFoundException


class TestCategoryOutputUnit:

    def test_fields(self):
        assert CategoryOutput.__annotations__, {
            'id': str,
            'name': str,
            'description': Optional[str],
            'is_active': bool,
            'created_at': datetime
        }

    def test_from_entity(self):
        category = Category.fake().a_category().build()
        output = CategoryOutput.from_entity(category)
        assert output.id == category.category_id.id
        assert output.name == category.name
        assert output.description == category.description
        assert output.is_active == category.is_active
        assert output.created_at == category.created_at


class TestCreateCategoryUseCaseUnit:

    use_case: CreateCategoryUseCase
    category_repo: CategoryInMemoryRepository

    def setup_method(self) -> None:
        self.category_repo = CategoryInMemoryRepository()
        self.use_case = CreateCategoryUseCase(self.category_repo)

    def test_if_instance_a_use_case(self):
        assert isinstance(self.use_case, UseCase)

    def test_input_annotation(self):
        assert CreateCategoryUseCase.Input.__annotations__, {
            'name': str,
            'description': Optional[str],
            'is_active': StrictBool
        }
        # pylint: disable=no-member
        description_field = CreateCategoryUseCase.Input.__dataclass_fields__[
            'description']
        assert description_field.default is None

        is_active_field = CreateCategoryUseCase.Input.__dataclass_fields__[
            'is_active']
        assert is_active_field.default is True

    def test_invalid_input(self):
        with pytest.raises(ValidationError) as assert_error:
            CreateCategoryUseCase.Input()  # pylint: disable=no-value-for-parameter #type: ignore
        assert len(assert_error.value.errors()) == 1
        name_error = assert_error.value.errors()[0]
        assert 'name' in name_error['loc']
        assert 'missing' in name_error['type']
        assert 'Field required' == name_error['msg']

        with pytest.raises(ValidationError) as assert_error:
            CreateCategoryUseCase.Input(
                name=1, description=1, is_active='invalid')  # type: ignore
        assert len(assert_error.value.errors()) == 3

        name_error = assert_error.value.errors()[0]
        assert 'name' in name_error['loc']
        assert 'string_type' in name_error['type']
        assert 'Input should be a valid string' == name_error['msg']

        description_error = assert_error.value.errors()[1]
        assert 'description' in description_error['loc']
        assert 'string_type' in description_error['type']
        assert 'Input should be a valid string' == description_error['msg']

        is_active_error = assert_error.value.errors()[2]
        assert 'is_active' in is_active_error['loc']
        assert 'bool_type' in is_active_error['type']
        assert 'Input should be a valid boolean' == is_active_error['msg']

    def test_output(self):
        assert issubclass(CreateCategoryUseCase.Output, CategoryOutput)

    def test_execute(self):

        with patch.object(
            self.category_repo,
            'insert',
            wraps=self.category_repo.insert
        ) as spy_insert:
            input_param = CreateCategoryUseCase.Input(name='Movie')
            output = self.use_case.execute(input_param)
            spy_insert.assert_called_once()
            assert output == CreateCategoryUseCase.Output(
                id=self.category_repo.items[0].category_id.id,
                name='Movie',
                description=None,
                is_active=True,
                created_at=self.category_repo.items[0].created_at
            )

        input_param = CreateCategoryUseCase.Input(
            name='Movie', description='some description', is_active=False)
        output = self.use_case.execute(input_param)
        assert output == CreateCategoryUseCase.Output(
            id=self.category_repo.items[1].category_id.id,
            name='Movie',
            description='some description',
            is_active=False,
            created_at=self.category_repo.items[1].created_at
        )

        input_param = CreateCategoryUseCase.Input(
            name='Movie', description='some description', is_active=True)
        output = self.use_case.execute(input_param)
        assert output == CreateCategoryUseCase.Output(
            id=self.category_repo.items[2].category_id.id,
            name='Movie',
            description='some description',
            is_active=True,
            created_at=self.category_repo.items[2].created_at
        )


class TestGetCategoryUseCaseUnit:

    use_case: GetCategoryUseCase
    category_repo: CategoryInMemoryRepository

    def setup_method(self) -> None:
        self.category_repo = CategoryInMemoryRepository()
        self.use_case = GetCategoryUseCase(self.category_repo)

    def test_if_instance_a_use_case(self):
        assert issubclass(GetCategoryUseCase, UseCase)

    def test_input(self):
        assert GetCategoryUseCase.Input.__annotations__, {
            'id': UUID,
        }

    def test_invalid_input(self):
        with pytest.raises(ValidationError) as assert_error:
            GetCategoryUseCase.Input('invalid_id')  # type: ignore
        assert 'Input should be a valid UUID' in assert_error.value.errors()[
            0]['msg']

    def test_throws_exception_when_category_not_found(self):
        input_param = GetCategoryUseCase.Input(
            '5f4b87a0-7b4a-4c1d-8e0a-0e8a0e9f1b9a')  # type: ignore
        with pytest.raises(NotFoundException) as assert_error:
            self.use_case.execute(input_param)
        assert assert_error.value.args[0] == "Category with id 5f4b87a0-7b4a-4c1d-8e0a-0e8a0e9f1b9a not found"

        input_param = GetCategoryUseCase.Input(uuid4())
        with pytest.raises(NotFoundException) as assert_error:
            self.use_case.execute(input_param)
        assert assert_error.value.args[0] == f"Category with id {input_param.id} not found"

    def test_output(self):
        assert issubclass(GetCategoryUseCase.Output, CategoryOutput)

    def test_execute(self):
        category = Category.fake().a_category().build()
        self.category_repo.items = [category]
        with patch.object(
            self.category_repo,
            'find_by_id',
            wraps=self.category_repo.find_by_id
        ) as spy_find_by_id:
            input_param = GetCategoryUseCase.Input(
                category.category_id.id)  # type: ignore
            output = self.use_case.execute(input_param)
            spy_find_by_id.assert_called_once()
            assert output == GetCategoryUseCase.Output(
                id=category.category_id.id,
                name=category.name,
                description=category.description,
                is_active=category.is_active,
                created_at=category.created_at
            )


class TestListCategoriesUseCase:

    use_case: ListCategoriesUseCase
    category_repo: CategoryInMemoryRepository

    def setup_method(self) -> None:
        self.category_repo = CategoryInMemoryRepository()
        self.use_case = ListCategoriesUseCase(self.category_repo)

    def test_instance_use_case(self):
        assert issubclass(ListCategoriesUseCase, UseCase)

    def test_input(self):
        assert issubclass(ListCategoriesUseCase.Input, SearchInput)

    def test_output(self):
        assert issubclass(ListCategoriesUseCase.Output, PaginationOutput)

    def test__to_output(self):

        default_props = {
            'total': 1,
            'current_page': 1,
            'per_page': 2,
        }

        result = ICategoryRepository.SearchResult(items=[], **default_props)
        output = self.use_case._ListCategoriesUseCase__to_output(   # pylint: disable=protected-access #type: ignore
            result
        )
        assert output == ListCategoriesUseCase.Output(
            items=[],
            total=1,
            current_page=1,
            per_page=2,
            last_page=1,
        )

        entity = Category.fake().a_category().build()
        result = ICategoryRepository.SearchResult(
            items=[entity], **default_props)
        output = self.use_case._ListCategoriesUseCase__to_output(  # pylint: disable=protected-access #type: ignore
            result)
        assert output == ListCategoriesUseCase.Output(
            items=[CategoryOutput.from_entity(entity)],
            total=1,
            current_page=1,
            per_page=2,
            last_page=1,
        )

    def test_execute_using_empty_search_params(self):
        items = [
            Category.fake().a_category().with_name('test 1').build(),
            Category.fake().a_category().with_name('test 2').with_created_at(
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=200)).build()
        ]
        self.category_repo.bulk_insert(items)
        with patch.object(
            self.category_repo,
            'search',
            wraps=self.category_repo.search
        ) as spy_search:
            input_param = ListCategoriesUseCase.Input()
            output = self.use_case.execute(input_param)
            spy_search.assert_called_once()
            assert output == ListCategoriesUseCase.Output(
                items=list(
                    map(CategoryOutput.from_entity,
                        self.category_repo.items[::-1])
                ),
                total=2,
                current_page=1,
                per_page=15,
                last_page=1
            )

    def test_execute_using_pagination_and_sort_and_filter(self):
        items = [
            Category.fake().a_category().with_name('a').build(),
            Category.fake().a_category().with_name('AAA').build(),
            Category.fake().a_category().with_name('AaA').build(),
            Category.fake().a_category().with_name('b').build(),
            Category.fake().a_category().with_name('c').build(),
        ]
        self.category_repo.bulk_insert(items)

        input_param = ListCategoriesUseCase.Input(
            page=1,
            per_page=2,
            sort='name',
            sort_dir='asc',
            filter='a'
        )
        output = self.use_case.execute(input_param)
        assert output == ListCategoriesUseCase.Output(
            items=list(
                map(CategoryOutput.from_entity,
                    [items[1], items[2]])
            ),
            total=3,
            current_page=1,
            per_page=2,
            last_page=2
        )

        input_param = ListCategoriesUseCase.Input(
            page=2,
            per_page=2,
            sort='name',
            sort_dir='asc',
            filter='a'
        )
        output = self.use_case.execute(input_param)
        assert output == ListCategoriesUseCase.Output(
            items=list(
                map(CategoryOutput.from_entity,
                    [items[0]])
            ),
            total=3,
            current_page=2,
            per_page=2,
            last_page=2
        )

        input_param = ListCategoriesUseCase.Input(
            page=1,
            per_page=2,
            sort='name',
            sort_dir='desc',
            filter='a'
        )
        output = self.use_case.execute(input_param)
        assert output == ListCategoriesUseCase.Output(
            items=list(
                map(CategoryOutput.from_entity,
                    [items[0], items[2]])
            ),
            total=3,
            current_page=1,
            per_page=2,
            last_page=2
        )

        input_param = ListCategoriesUseCase.Input(
            page=2,
            per_page=2,
            sort='name',
            sort_dir='desc',
            filter='a'
        )
        output = self.use_case.execute(input_param)
        assert output == ListCategoriesUseCase.Output(
            items=list(
                map(CategoryOutput.from_entity,
                    [items[1]])
            ),
            total=3,
            current_page=2,
            per_page=2,
            last_page=2
        )


class TestUpdateCategoryUseCase:

    use_case: UpdateCategoryUseCase
    category_repo: CategoryInMemoryRepository

    def setup_method(self) -> None:
        self.category_repo = CategoryInMemoryRepository()
        self.use_case = UpdateCategoryUseCase(self.category_repo)

    def test_instance_use_case(self):
        assert isinstance(self.use_case, UseCase)

    def test_invalid_input(self):
        with pytest.raises(ValidationError) as assert_error:
            UpdateCategoryUseCase.Input()  # pylint: disable=no-value-for-parameter #type: ignore
        assert len(assert_error.value.errors()) == 1
        assert 'id' in assert_error.value.errors()[0]['loc']
        assert 'missing' in assert_error.value.errors()[0]['type']
        assert 'Field required' in assert_error.value.errors()[
            0]['msg']

        with pytest.raises(ValidationError) as assert_error:
            UpdateCategoryUseCase.Input(
                id=1, name=1, description=1, is_active='invalid')  # type: ignore
        assert len(assert_error.value.errors()) == 4

        uuid_error = assert_error.value.errors()[0]
        assert 'id' in uuid_error['loc']
        assert 'uuid_type' in uuid_error['type']
        assert 'UUID input should be a string, bytes or UUID object' in uuid_error['msg']

        name_error = assert_error.value.errors()[1]
        assert 'name' in name_error['loc']
        assert 'string_type' in name_error['type']
        assert 'Input should be a valid string' in name_error['msg']

        description_error = assert_error.value.errors()[2]
        assert 'description' in description_error['loc']
        assert 'string_type' in description_error['type']
        assert 'Input should be a valid string' in description_error['msg']

        is_active_error = assert_error.value.errors()[3]
        assert 'is_active' in is_active_error['loc']
        assert 'bool_type' in is_active_error['type']
        assert 'Input should be a valid boolean' in is_active_error['msg']

    def test_input(self):
        assert UpdateCategoryUseCase.Input.__annotations__, {
            'id': UUID,
            'name': Optional[str],
            'description': Optional[str],
            'is_active': Optional[bool]
        }

        # # pylint: disable=no-member
        description_field = UpdateCategoryUseCase.Input.__dataclass_fields__[
            'description']
        assert description_field.default.default is MISSING

        is_active_field = UpdateCategoryUseCase.Input.__dataclass_fields__[
            'is_active']
        assert is_active_field.default is None

    def test_output(self):
        assert issubclass(UpdateCategoryUseCase.Output, CategoryOutput)

    def test_throw_exception_when_category_not_found(self):
        _id = uuid4()
        request = UpdateCategoryUseCase.Input(id=_id)
        with pytest.raises(NotFoundException) as assert_error:
            self.use_case.execute(request)
        assert assert_error.value.args[0] == f"Category with id {str(_id)} not found"

    # Defina a fixture dentro da classe
    @pytest.fixture
    def execute_fixture(self, request: SubRequest):
        entity = request.param['entity']
        self.category_repo.insert(entity)

        input_param = UpdateCategoryUseCase.Input(
            id=entity.category_id.id,  # type: ignore
            **request.param['input']
        )

        output_dict = {
            'id': entity.category_id.id,  # type: ignore
            'name': entity.name,
            'description': entity.description,
            'is_active': entity.is_active,
            'created_at': entity.created_at
        }

        output_dict |= request.param['expected_output']

        output = UpdateCategoryUseCase.Output(**output_dict)

        yield (input_param, output)

    @pytest.mark.parametrize(
        'execute_fixture',
        (
            pytest.param({
                'entity': Category.fake().a_category().build(),
                'input': {},
                'expected_output': {}
            }, id='empty'),
            pytest.param({
                'entity': Category.fake().a_category().build(),
                'input': {
                    'name': 'test 2',
                    'description': 'test description',
                },
                'expected_output': {
                    'name': 'test 2',
                    'description': 'test description',
                }
            }, id='name and description'),
            pytest.param({
                'entity': Category.fake().a_category().build(),
                'input': {
                    'name': 'test',
                },
                'expected_output': {
                    'name': 'test',
                }
            }, id='only name'),
            pytest.param({
                'entity': Category.fake().a_category().build(),
                'input': {
                    'is_active': False,
                },
                'expected_output': {
                    'is_active': False,
                }
            }, id='only is_active')
        ),
        indirect=True
    )
    def test_execute(self, execute_fixture: Tuple[UpdateCategoryUseCase.Input, UpdateCategoryUseCase.Output]):
        input_param, expected_output = execute_fixture
        output = self.use_case.execute(input_param)
        assert output == expected_output


class TestDeleteCategoryUseCase:

    use_case: DeleteCategoryUseCase
    category_repo: CategoryInMemoryRepository

    def setup_method(self) -> None:
        self.category_repo = CategoryInMemoryRepository()
        self.use_case = DeleteCategoryUseCase(self.category_repo)

    def test_instance_use_case(self):
        assert issubclass(DeleteCategoryUseCase, UseCase)

    def test_input(self):
        assert DeleteCategoryUseCase.Input.__annotations__, {
            'id': UUID,
        }

    def test_invalid_input(self):
        with pytest.raises(ValidationError) as assert_error:
            DeleteCategoryUseCase.Input('invalid_id')  # type: ignore
        assert 'Input should be a valid UUID' in assert_error.value.errors()[
            0]['msg']

    def test_throws_exception_when_category_not_found(self):
        input_param = DeleteCategoryUseCase.Input(
            '5f4b87a0-7b4a-4c1d-8e0a-0e8a0e9f1b9a')  # type: ignore
        with pytest.raises(NotFoundException) as assert_error:
            self.use_case.execute(input_param)
        assert assert_error.value.args[0] == "Category with id 5f4b87a0-7b4a-4c1d-8e0a-0e8a0e9f1b9a not found"

        input_param = DeleteCategoryUseCase.Input(uuid4())
        with pytest.raises(NotFoundException) as assert_error:
            self.use_case.execute(input_param)
        assert assert_error.value.args[0] == f"Category with id {input_param.id} not found"

    def test_execute(self):
        category = Category.fake().a_category().build()
        self.category_repo.items = [category]
        with patch.object(
            self.category_repo,
            'delete',
            wraps=self.category_repo.delete
        ) as spy_delete:
            request = DeleteCategoryUseCase.Input(
                id=category.category_id.id)  # type: ignore
            self.use_case.execute(request)
            spy_delete.assert_called_once()
            assert len(self.category_repo.items) == 0
