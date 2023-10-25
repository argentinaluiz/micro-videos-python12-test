import datetime
from typing import Tuple, cast
from uuid import uuid4
import pytest

from core.category.application.use_cases import CreateCategoryUseCase, DeleteCategoryUseCase, GetCategoryUseCase, ListCategoriesUseCase, UpdateCategoryUseCase
from core.category.domain.entities import Category, CategoryId
from core.category.domain.repositories import ICategoryRepository
from core.shared.domain.exceptions import EntityValidationException, NotFoundException
from django_app.category_app.models import CategoryDjangoRepository
from _pytest.fixtures import SubRequest


@pytest.mark.django_db
class TestIntCreateCategoryUse:

    use_case: CreateCategoryUseCase
    repo: CategoryDjangoRepository

    def setup_method(self) -> None:
        self.repo = CategoryDjangoRepository()
        self.use_case = CreateCategoryUseCase(self.repo)

    def test_execute(self):
        input_param = CreateCategoryUseCase.Input(name='Movie1')
        output = self.use_case.execute(input_param)
        entity = cast(Category, self.repo.find_by_id(CategoryId(output.id)))

        assert output == CreateCategoryUseCase.Output(
            id=entity.category_id.id,
            name='Movie1',
            description=None,
            is_active=True,
            created_at=entity.created_at
        )
        assert entity.name == 'Movie1'
        assert entity.description is None
        assert entity.is_active

        input_param = CreateCategoryUseCase.Input(
            name='Movie2',
            description='some description'
        )
        output = self.use_case.execute(input_param)
        entity = cast(Category, self.repo.find_by_id(CategoryId(output.id)))

        assert output == CreateCategoryUseCase.Output(
            id=entity.category_id.id,
            name='Movie2',
            description='some description',
            is_active=True,
            created_at=entity.created_at
        )
        assert entity.name == 'Movie2'
        assert entity.description == 'some description'
        assert entity.is_active

        input_param = CreateCategoryUseCase.Input(
            name='Movie3',
            description='some description',
            is_active=True
        )
        output = self.use_case.execute(input_param)
        entity = cast(Category, self.repo.find_by_id(CategoryId(output.id)))

        assert output == CreateCategoryUseCase.Output(
            id=entity.category_id.id,
            name='Movie3',
            description='some description',
            is_active=True,
            created_at=entity.created_at
        )
        assert entity.name == 'Movie3'
        assert entity.description == 'some description'
        assert entity.is_active

        input_param = CreateCategoryUseCase.Input(
            name='Movie4',
            description='some description ##',
            is_active=False
        )
        output = self.use_case.execute(input_param)
        entity = cast(Category, self.repo.find_by_id(CategoryId(output.id)))

        assert output == CreateCategoryUseCase.Output(
            id=entity.category_id.id,
            name='Movie4',
            description='some description ##',
            is_active=False,
            created_at=entity.created_at
        )
        assert entity.name == 'Movie4'
        assert entity.description == 'some description ##'
        assert not entity.is_active


@pytest.mark.django_db
class TestIntGetCategoryUseCase:

    use_case: GetCategoryUseCase
    repo: CategoryDjangoRepository

    def setup_method(self) -> None:
        self.repo = CategoryDjangoRepository()
        self.use_case = GetCategoryUseCase(self.repo)

    def test_throws_exception_when_category_not_found(self):
        _id = uuid4()
        input_param = GetCategoryUseCase.Input(_id)
        with pytest.raises(NotFoundException) as assert_error:
            self.use_case.execute(input_param)
        assert str(assert_error.value) == str(NotFoundException(
            _id, Category.__name__
        ))

    def test_execute(self):
        entity = Category.fake().a_category().build()
        self.repo.insert(entity)
        input_param = GetCategoryUseCase.Input(
            entity.category_id.id)  # type: ignore
        output = self.use_case.execute(input_param)
        assert output == GetCategoryUseCase.Output(
            id=entity.category_id.id,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
            created_at=entity.created_at
        )


@pytest.mark.django_db
class TestIntListCategoriesUseCaseInt:

    use_case: ListCategoriesUseCase
    repo: CategoryDjangoRepository

    def setup_method(self) -> None:
        self.repo = CategoryDjangoRepository()
        self.use_case = ListCategoriesUseCase(self.repo)

    def test_execute_using_empty_search_params(self):
        categories = Category.fake()\
            .the_categories(2)\
            .with_created_at(
            lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=index)
        ).build()
        self.repo.bulk_insert(categories)
        input_param = ListCategoriesUseCase.Input()
        output = self.use_case.execute(input_param)
        assert output == self.use_case._ListCategoriesUseCase__to_output(  # type: ignore #pylint: disable=protected-access
            ICategoryRepository.SearchResult(
                items=[
                    categories[1],
                    categories[0],
                ],
                total=2,
                current_page=1,
                per_page=15,
            ))

    def test_execute_using_pagination_and_sort_and_filter(self):
        faker = Category.fake().a_category()
        entities = [
            faker.with_name('a').build(),
            faker.with_name('AAA').build(),
            faker.with_name('AaA').build(),
            faker.with_name('b').build(),
            faker.with_name('c').build(),
        ]
        self.repo.bulk_insert(entities)

        input_param = ListCategoriesUseCase.Input(
            page=1,
            per_page=2,
            sort='name',
            sort_dir='asc',
            filter='a'
        )
        output = self.use_case.execute(input_param)
        assert output == self.use_case._ListCategoriesUseCase__to_output(  # type: ignore #pylint: disable=protected-access
            ICategoryRepository.SearchResult(
                items=[
                    entities[1],
                    entities[2],
                ],
                total=3,
                current_page=1,
                per_page=2,
            ))

        input_param = ListCategoriesUseCase.Input(
            page=2,
            per_page=2,
            sort='name',
            sort_dir='asc',
            filter='a'
        )
        output = self.use_case.execute(input_param)
        assert output == self.use_case._ListCategoriesUseCase__to_output(  # type: ignore #pylint: disable=protected-access
            ICategoryRepository.SearchResult(
                items=[
                    entities[0],
                ],
                total=3,
                current_page=2,
                per_page=2,
            ))

        input_param = ListCategoriesUseCase.Input(
            page=1,
            per_page=2,
            sort='name',
            sort_dir='desc',
            filter='a'
        )
        output = self.use_case.execute(input_param)
        assert output == self.use_case._ListCategoriesUseCase__to_output(  # type: ignore #pylint: disable=protected-access
            ICategoryRepository.SearchResult(
                items=[
                    entities[0],
                    entities[2],
                ],
                total=3,
                current_page=1,
                per_page=2,
            ))

        input_param = ListCategoriesUseCase.Input(
            page=2,
            per_page=2,
            sort='name',
            sort_dir='desc',
            filter='a'
        )
        output = self.use_case.execute(input_param)
        assert output == self.use_case._ListCategoriesUseCase__to_output(  # type: ignore #pylint: disable=protected-access
            ICategoryRepository.SearchResult(
                items=[
                    entities[1],
                ],
                total=3,
                current_page=2,
                per_page=2,
            ))


@pytest.mark.django_db
class TestIntUpdateCategoryUseCase:

    use_case: UpdateCategoryUseCase
    repo: CategoryDjangoRepository

    def setup_method(self) -> None:
        self.repo = CategoryDjangoRepository()
        self.use_case = UpdateCategoryUseCase(self.repo)

    def test_throw_exception_when_category_not_found(self):
        _id = uuid4()
        request = UpdateCategoryUseCase.Input(id=_id, name='test')
        with pytest.raises(NotFoundException) as assert_error:
            self.use_case.execute(request)
        assert str(assert_error.value) == str(NotFoundException(
            _id, Category.__name__
        ))

    def test_throw_exception_when_name_is_too_long(self):
        entity = Category.fake().a_category().build()
        self.repo.insert(entity)
        request = UpdateCategoryUseCase.Input(
            id=entity.category_id.id,  # type: ignore
            name='t' * 256
        )
        with pytest.raises(EntityValidationException):
            self.use_case.execute(request)

    @pytest.fixture
    def execute_fixture(self, request: SubRequest):
        entity = request.param['entity']
        self.repo.insert(entity)

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


@pytest.mark.django_db
class TestIntDeleteCategoryUseCase:

    use_case: DeleteCategoryUseCase
    repo: CategoryDjangoRepository

    def setup_method(self) -> None:
        self.repo = CategoryDjangoRepository()
        self.use_case = DeleteCategoryUseCase(self.repo)

    def test_throw_exception_when_category_not_found(self):
        _id = uuid4()
        request = DeleteCategoryUseCase.Input(_id)
        with pytest.raises(NotFoundException) as assert_error:
            self.use_case.execute(request)
        assert str(assert_error.value) == str(NotFoundException(
            _id, Category.__name__
        ))

    def test_execute(self):
        entity = Category.fake().a_category().build()
        self.repo.insert(entity)
        request = DeleteCategoryUseCase.Input(
            id=entity.category_id.id)  # type: ignore
        self.use_case.execute(request)

        assert self.repo.find_by_id(entity.category_id) is None
