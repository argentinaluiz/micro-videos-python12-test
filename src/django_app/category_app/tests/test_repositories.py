import datetime
import pytest
from core.category.domain.entities import Category
from core.category.domain.repositories import ICategoryRepository
from core.shared.domain.exceptions import NotFoundException
from core.shared.domain.value_objects import Uuid
from django_app.category_app.models import CategoryDjangoRepository, CategoryModel


@pytest.mark.django_db
class TestCategoryDjangoRepository:

    repo: CategoryDjangoRepository

    def setup_method(self):
        self.repo = CategoryDjangoRepository()  # pylint: disable=abstract-class-instantiated

    def test_insert(self):
        category = Category.fake().a_category().build()

        self.repo.insert(category)

        model = CategoryModel.objects.get(pk=category.category_id.id)

        assert str(model.id) == category.category_id.id
        assert model.name == category.name
        assert model.description == category.description
        assert model.is_active == category.is_active
        assert model.created_at == category.created_at

        category = Category(
            name='Movie 2',
            description='Movie description',
            is_active=False
        )

        self.repo.insert(category)

        model = CategoryModel.objects.get(pk=category.entity_id.id)

        assert str(model.id) == category.entity_id.id
        assert model.name == 'Movie 2'
        assert model.description == 'Movie description'
        assert model.is_active == False
        assert model.created_at == category.created_at

    def test_bulk_insert(self):
        categories = Category.fake().the_categories(2)\
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=index))\
            .build()

        self.repo.bulk_insert(categories)

        models = CategoryModel.objects.all()

        assert len(models) == 2
        assert str(models[0].id) == categories[1].category_id.id
        assert models[0].name == categories[1].name
        assert models[0].description == categories[1].description
        assert models[0].is_active == categories[1].is_active
        assert models[0].created_at == categories[1].created_at

        assert str(models[1].id) == categories[0].category_id.id
        assert models[1].name == categories[0].name
        assert models[1].description == categories[0].description
        assert models[1].is_active == categories[0].is_active
        assert models[1].created_at == categories[0].created_at

    def test_find_by_id(self):

        assert self.repo.find_by_id(Uuid()) is None

        category = Category(
            name='Movie',
        )
        self.repo.insert(category)

        category_found = self.repo.find_by_id(category.category_id)
        assert category_found == category

    def test_find_all(self):
        categories = Category.fake().the_categories(2)\
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=index))\
            .build()
        self.repo.bulk_insert(categories)
        found_categories = self.repo.find_all()

        assert len(found_categories) == 2
        assert found_categories[0].category_id == categories[1].category_id
        assert found_categories[0].name == categories[1].name
        assert found_categories[0].description == categories[1].description
        assert found_categories[0].is_active == categories[1].is_active
        assert found_categories[0].created_at == categories[1].created_at

        assert found_categories[1].category_id == categories[0].category_id
        assert found_categories[1].name == categories[0].name
        assert found_categories[1].description == categories[0].description
        assert found_categories[1].is_active == categories[0].is_active
        assert found_categories[1].created_at == categories[0].created_at

    def test_throw_not_found_exception_in_update(self):
        category = Category.fake().a_category().build()
        with pytest.raises(NotFoundException) as assert_error:
            self.repo.update(category)
        assert assert_error.value.args[0] == f"Category with id {category.category_id.id} not found"

    def test_update(self):
        category = Category.fake().a_category().build()
        self.repo.insert(category)

        category.change_name('Movie changed')
        category.change_description('description changed')
        category.deactivate()

        self.repo.update(category)

        model = CategoryModel.objects.get(pk=category.category_id.id)

        assert str(model.id) == category.category_id.id
        assert model.name == category.name
        assert model.description == category.description
        assert model.is_active == category.is_active
        assert model.created_at == category.created_at

    def test_throw_not_found_exception_in_delete(self):
        category_id = Uuid()
        with pytest.raises(NotFoundException) as assert_error:
            self.repo.delete(category_id)
        assert assert_error.value.args[0] == f"Category with id {category_id.id} not found"

    def test_delete(self):
        category = Category.fake().a_category().build()
        self.repo.insert(category)

        self.repo.delete(category.category_id)

        assert CategoryModel.objects.filter(
            pk=category.category_id.id).count() == 0

    def test_search_when_params_is_empty(self):
        entities = Category.fake().the_categories(16).with_created_at(
            lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=index)
        ).build()
        self.repo.bulk_insert(entities)
        entities.reverse()

        search_result = self.repo.search(ICategoryRepository.SearchParams())
        assert search_result == ICategoryRepository.SearchResult(
            items=entities[:15],
            total=16,
            current_page=1,
            per_page=15,
        )

    def test_search_applying_filter_and_paginate(self):
        created_at = datetime.datetime.now(datetime.timezone.utc)
        entities = [
            Category.fake().a_category().with_name(
                'test').with_created_at(created_at + datetime.timedelta(days=4)).build(),
            Category.fake().a_category().with_name('a').with_created_at(created_at + datetime.timedelta(days=3)).build(),
            Category.fake().a_category().with_name(
                'TEST').with_created_at(created_at + datetime.timedelta(days=2)).build(),
            Category.fake().a_category().with_name(
                'TeSt').with_created_at(created_at + datetime.timedelta(days=1)).build(),
        ]
        self.repo.bulk_insert(entities)
        search_params = ICategoryRepository.SearchParams(
            init_page=1,
            init_per_page=2,
            init_filter='E'
        )
        search_result = self.repo.search(search_params)
        assert search_result == ICategoryRepository.SearchResult(
            items=[
                entities[0],
                entities[2],
            ],
            total=3,
            current_page=1,
            per_page=2,
        )

    @pytest.mark.parametrize(
        'search_params, expected_search_output',
        [
            pytest.param(
                ICategoryRepository.SearchParams(
                    init_per_page=2,
                    init_sort='name',
                ),
                ICategoryRepository.SearchResult(
                    items=[
                        1, 0  # type: ignore
                    ],
                    total=5,
                    current_page=1,
                    per_page=2,
                ),
                id='asc sort, page = 1',
            ),
            pytest.param(
                ICategoryRepository.SearchParams(
                    init_page=2,
                    init_per_page=2,
                    init_sort='name',
                ),
                ICategoryRepository.SearchResult(
                    items=[
                        4, 2  # type: ignore
                    ],
                    total=5,
                    current_page=2,
                    per_page=2,
                ),
                id='asc sort, page = 2',
            ),
            pytest.param(
                ICategoryRepository.SearchParams(
                    init_per_page=2,
                    init_sort='name',
                    init_sort_dir='desc',
                ),
                ICategoryRepository.SearchResult(
                    items=[
                        3, 2  # type: ignore
                    ],
                    total=5,
                    current_page=1,
                    per_page=2,
                ),
                id='desc sort, page = 1',
            ),
            pytest.param(
                ICategoryRepository.SearchParams(
                    init_page=2,
                    init_per_page=2,
                    init_sort='name',
                    init_sort_dir='desc',
                ),
                ICategoryRepository.SearchResult(
                    items=[
                        4, 0  # type: ignore
                    ],
                    total=5,
                    current_page=2,
                    per_page=2,
                ),
                id='desc sort, page = 2',
            ),
        ]
    )
    def test_search_applying_paginate_and_sort(
            self,
            search_params: ICategoryRepository.SearchParams,
            expected_search_output: ICategoryRepository.SearchResult):
        entities = [
            Category.fake().a_category().with_name('b').build(),
            Category.fake().a_category().with_name('a').build(),
            Category.fake().a_category().with_name('d').build(),
            Category.fake().a_category().with_name('e').build(),
            Category.fake().a_category().with_name('c').build(),
        ]
        self.repo.bulk_insert(entities)

        search_result = self.repo.search(search_params)
        expected_search_output.items = [entities[i]  # type: ignore
                                        for i in expected_search_output.items]
        assert search_result == expected_search_output

    def test_search_applying_filter_sort_and_paginate(self):
        entities = [
            Category.fake().a_category().with_name('test').build(),
            Category.fake().a_category().with_name('a').build(),
            Category.fake().a_category().with_name('TEST').build(),
            Category.fake().a_category().with_name('e').build(),
            Category.fake().a_category().with_name('TeSt').build(),
        ]

        self.repo.bulk_insert(entities)

        search_result = self.repo.search(ICategoryRepository.SearchParams(
            init_page=1,
            init_per_page=2,
            init_sort='name',
            init_sort_dir='asc',
            init_filter='TEST'
        ))
        assert search_result == ICategoryRepository.SearchResult(
            items=[
                entities[2],
                entities[4],
            ],
            total=3,
            current_page=1,
            per_page=2,
        )

        search_result = self.repo.search(ICategoryRepository.SearchParams(
            init_page=2,
            init_per_page=2,
            init_sort='name',
            init_sort_dir='asc',
            init_filter='TEST'
        ))
        assert search_result == ICategoryRepository.SearchResult(
            items=[
                entities[0],
            ],
            total=3,
            current_page=2,
            per_page=2,
        )
