import datetime
from typing import Any, Dict
from core.category.domain.entities import Category, CategoryId
from django_app.category_app.models import CategoryDjangoRepository
import pytest
from core.genre.domain.entities import Genre, GenreId
from core.genre.domain.repositories import GenreFilter, IGenreRepository
from core.shared.domain.exceptions import NotFoundException
from django_app.genre_app.models import GenreDjangoRepository, GenreModel


@pytest.mark.django_db
class TestGenreDjangoRepository:

    genre_repo: GenreDjangoRepository
    category_repo: CategoryDjangoRepository

    def setup_method(self):
        self.genre_repo = GenreDjangoRepository()
        self.category_repo = CategoryDjangoRepository()

    def test_insert(self):
        categories = Category.fake().the_categories(2).build()
        self.category_repo.bulk_insert(categories)
        genre = Genre.fake().a_genre()\
            .add_category_id(categories[0].category_id)\
            .add_category_id(categories[1].category_id)\
            .build()

        self.genre_repo.insert(genre)

        model = GenreModel.objects.get(pk=genre.genre_id.id)

        categories_models = model.categories.all()
        assert str(model.id) == genre.genre_id.id
        assert model.name == genre.name
        assert categories[0].category_id.id in [
            str(category.id) for category in categories_models]
        assert categories[1].category_id.id in [
            str(category.id) for category in categories_models]
        assert model.is_active == genre.is_active
        assert model.created_at == genre.created_at

    def test_bulk_insert(self):
        category = Category.fake().the_categories(2).build()
        self.category_repo.bulk_insert(category)
        genres = Genre.fake().the_genres(2).build()

        genres[0].add_category_id(category[0].category_id)
        genres[1].add_category_id(category[1].category_id)

        self.genre_repo.bulk_insert(genres)

        model1 = GenreModel.objects.get(pk=genres[0].genre_id.id)

        assert str(model1.id) == genres[0].genre_id.id
        assert model1.name == genres[0].name
        assert str(model1.categories.all()[0].id) == category[0].category_id.id
        assert model1.is_active == genres[0].is_active
        assert model1.created_at == genres[0].created_at

        model2 = GenreModel.objects.get(pk=genres[1].genre_id.id)

        assert str(model2.id) == genres[1].genre_id.id
        assert model2.name == genres[1].name
        assert str(model2.categories.all()[0].id) == category[1].category_id.id
        assert model2.is_active == genres[1].is_active
        assert model2.created_at == genres[1].created_at

    def test_find_by_id(self):

        assert self.genre_repo.find_by_id(GenreId()) is None

        categories = Category.fake().the_categories(2).build()
        self.category_repo.bulk_insert(categories)
        genre = Genre.fake().a_genre()\
            .add_category_id(categories[0].category_id)\
            .add_category_id(categories[1].category_id)\
            .build()
        self.genre_repo.insert(genre)

        genre_found = self.genre_repo.find_by_id(genre.genre_id)
        assert genre_found == genre

    def test_find_all(self):
        categories = Category.fake().the_categories(2).build()
        self.category_repo.bulk_insert(categories)
        genres = Genre.fake().the_genres(2)\
            .with_created_at(lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=index))\
            .build()

        genres[0].add_category_id(categories[0].category_id)
        genres[0].remove_category_id(list(genres[0].categories_id)[1])
        genres[1].add_category_id(categories[1].category_id)
        genres[1].remove_category_id(list(genres[1].categories_id)[1])
        #print(genres)
        self.genre_repo.bulk_insert(genres)

        # found_genres = self.genre_repo.find_all()

        # assert len(found_genres) == 2
        # assert found_genres[0] == genres[1]
        # assert found_genres[1] == genres[0]

    def test_throw_not_found_exception_in_update(self):
        genre = Genre.fake().a_genre().build()
        with pytest.raises(NotFoundException) as assert_error:
            self.genre_repo.update(genre)
        assert assert_error.value.args[
            0] == f"Genre with id {genre.genre_id.id} not found"

    def test_update(self):
        categories = Category.fake().the_categories(2).build()
        self.category_repo.bulk_insert(categories)
        genre = Genre.fake().a_genre().add_category_id(
            categories[0].category_id).build()
        self.genre_repo.insert(genre)

        genre.change_name('Movie changed')
        genre.deactivate()
        genre.sync_categories_id({categories[1].category_id})

        # from django.db import connection
        # from django.test.utils import CaptureQueriesContext

        # with CaptureQueriesContext(connection) as ctx:
        self.genre_repo.update(genre)
        # print(ctx.captured_queries)

        model = GenreModel.objects.get(pk=genre.genre_id.id)

        assert str(model.id) == genre.genre_id.id
        assert model.name == genre.name
        categories_models = model.categories.all()
        assert len(categories_models) == 1
        assert categories[1].category_id.id == str(categories_models[0].id)
        assert model.is_active == genre.is_active
        assert model.created_at == genre.created_at

    def test_throw_not_found_exception_in_delete(self):
        genre_id = GenreId()
        with pytest.raises(NotFoundException) as assert_error:
            self.genre_repo.delete(genre_id)
        assert assert_error.value.args[0] == f"Genre with id {genre_id.id} not found"

    def test_delete(self):
        categories = Category.fake().the_categories(2).build()
        self.category_repo.bulk_insert(categories)
        genre = Genre.fake().a_genre().add_category_id(
            categories[0].category_id).build()
        self.genre_repo.insert(genre)

        # from django.db import connection
        # from django.test.utils import CaptureQueriesContext

        # with CaptureQueriesContext(connection) as ctx:
        self.genre_repo.delete(genre.genre_id)
        # print(ctx.captured_queries)

        assert GenreModel.objects.filter(
            pk=genre.genre_id.id).count() == 0

    def test_search_when_params_is_empty(self):
        categories = Category.fake().the_categories(2).build()
        self.category_repo.bulk_insert(categories)
        entities = Genre.fake().the_genres(16)\
            .add_category_id(categories[0].category_id)\
            .add_category_id(categories[1].category_id)\
            .with_created_at(
            lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=index)
        )\
            .build()
        self.genre_repo.bulk_insert(entities)
        entities.reverse()

        search_result = self.genre_repo.search(IGenreRepository.SearchParams())
        assert search_result == IGenreRepository.SearchResult(
            items=entities[:15],
            total=16,
            current_page=1,
            per_page=15,
        )

    def test_search_applying_paginate_and_filter_by_name(self):
        categories = Category.fake().the_categories(2).build()
        self.category_repo.bulk_insert(categories)
        genres = [
            Genre.fake().a_genre()
            .with_name('test')
            .add_category_id(categories[0].category_id)
            .add_category_id(categories[1].category_id)
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=4)
            )
            .build(),
            Genre.fake().a_genre()
            .with_name('a')
            .add_category_id(categories[0].category_id)
            .add_category_id(categories[1].category_id)
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=3)
            )
            .build(),
            Genre.fake().a_genre()
            .with_name('TEST')
            .add_category_id(categories[0].category_id)
            .add_category_id(categories[1].category_id)
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=2)
            )
            .build(),
            Genre.fake().a_genre()
            .with_name('TeSt')
            .add_category_id(categories[0].category_id)
            .add_category_id(categories[1].category_id)
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=1)
            )
            .build(),
        ]
        self.genre_repo.bulk_insert(genres)

        search_params = IGenreRepository.SearchParams(
            init_page=1,
            init_per_page=2,
            init_filter=GenreFilter(name='E')
        )
        search_result = self.genre_repo.search(search_params)
        print(search_result)
        assert search_result == IGenreRepository.SearchResult(
            items=[
                genres[0],
                genres[2],
            ],
            total=3,
            current_page=1,
            per_page=2,
        )

    @pytest.mark.parametrize('search_params, expected_search_output', [
        pytest.param(
            {
                'init_page': 1,
                'init_per_page': 2,
                'init_filter': {
                    'categories_id': [0]
                }
            },
            {
                'items': [2, 1],
                'total': 3,
                'current_page': 1,
                'per_page': 2,
            },
            id='filter by categories_id = [0], page = 1'
        ),
        pytest.param(
            {
                'init_page': 2,
                'init_per_page': 2,
                'init_filter': {
                    'categories_id': [0]
                }
            },
            {
                'items': [0],
                'total': 3,
                'current_page': 2,
                'per_page': 2,
            },
            id='filter by categories_id = [0], page = 2'
        ),
        pytest.param(
            {
                'init_page': 1,
                'init_per_page': 2,
                'init_filter': {
                    'categories_id': [0, 1]
                }
            },
            {
                'items': [4, 2],
                'total': 4,
                'current_page': 1,
                'per_page': 2,
            },
            id='filter by categories_id = [0, 1], page = 1'
        ),
        pytest.param(
            {
                'init_page': 2,
                'init_per_page': 2,
                'init_filter': {
                    'categories_id': [0, 1]
                }
            },
            {
                'items': [1, 0],
                'total': 4,
                'current_page': 2,
                'per_page': 2,
            },
            id='filter by categories_id = [0, 1], page = 2'
        ),
    ])
    def test_search_applying_paginate_and_filter_by_categories_id(self,
                                                                  search_params: Dict[str, Any],
                                                                  expected_search_output: Dict[str, Any]):
        categories = Category.fake().the_categories(4).build()
        self.category_repo.bulk_insert(categories)
        genres = [
            Genre.fake().a_genre()
            .add_category_id(categories[0].category_id)
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=1)
            )
            .build(),
            Genre.fake().a_genre()
            .add_category_id(categories[0].category_id)
            .add_category_id(categories[1].category_id)
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=2)
            )
            .build(),
            Genre.fake().a_genre()
            .add_category_id(categories[0].category_id)
            .add_category_id(categories[1].category_id)
            .add_category_id(categories[2].category_id)
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=4)
            )
            .build(),
            Genre.fake().a_genre()
            .add_category_id(categories[3].category_id)
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=5)
            )
            .build(),
            Genre.fake().a_genre()
            .add_category_id(categories[1].category_id)
            .add_category_id(categories[2].category_id)
            .with_created_at(
                datetime.datetime.now(
                    datetime.timezone.utc) + datetime.timedelta(days=6)
            )
            .build(),
        ]
        self.genre_repo.bulk_insert(genres)

        # from django.db import connection
        # from django.test.utils import CaptureQueriesContext

        # with CaptureQueriesContext(connection) as ctx:
        search_result = self.genre_repo.search(
            IGenreRepository.SearchParams(
                init_page=search_params['init_page'],
                init_per_page=search_params['init_per_page'],
                init_filter=GenreFilter(
                    categories_id={
                        categories[index].category_id
                        for index in search_params['init_filter']['categories_id']
                    }
                ),
            )
        )
        # print(ctx.captured_queries)
        expected_search_output['items'] = [genres[i]  # type: ignore
                                           for i in expected_search_output['items']]
        assert search_result == IGenreRepository.SearchResult(
            **expected_search_output)

    @pytest.mark.parametrize('search_params, expected_search_output', [
        pytest.param(
            IGenreRepository.SearchParams(
                init_per_page=2,
                init_sort='name'
            ),
            IGenreRepository.SearchResult(
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
            IGenreRepository.SearchParams(
                init_page=2,
                init_per_page=2,
                init_sort='name'
            ),
            IGenreRepository.SearchResult(
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
            IGenreRepository.SearchParams(
                init_per_page=2,
                init_sort='name',
                init_sort_dir='desc'
            ),
            IGenreRepository.SearchResult(
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
            IGenreRepository.SearchParams(
                init_page=2,
                init_per_page=2,
                init_sort='name',
                init_sort_dir='desc'
            ),
            IGenreRepository.SearchResult(
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
                                               search_params: IGenreRepository.SearchParams,
                                               expected_search_output: IGenreRepository.SearchResult):
        categories = Category.fake().the_categories(2).build()
        self.category_repo.bulk_insert(categories)
        genres = [
            Genre.fake().a_genre().add_category_id(
                categories[0].category_id).add_category_id(
                    categories[1].category_id).with_name('b').build(),
            Genre.fake().a_genre().add_category_id(
                categories[0].category_id).add_category_id(
                    categories[1].category_id).with_name('a').build(),
            Genre.fake().a_genre().add_category_id(
                categories[0].category_id).add_category_id(
                    categories[1].category_id).with_name('d').build(),
            Genre.fake().a_genre().add_category_id(
                categories[0].category_id).add_category_id(
                    categories[1].category_id).with_name('e').build(),
            Genre.fake().a_genre().add_category_id(
                categories[0].category_id).add_category_id(
                    categories[1].category_id).with_name('c').build(),
        ]
        self.genre_repo.bulk_insert(genres)

        search_result = self.genre_repo.search(search_params)
        expected_search_output.items = [genres[i]  # type: ignore
                                        for i in expected_search_output.items]
        assert search_result == expected_search_output

    @pytest.mark.parametrize('search_params, expected_search_output', [
        pytest.param(
            IGenreRepository.SearchParams(
                init_page=1,
                init_per_page=2,
                init_sort='name',
                init_filter=GenreFilter(name='TEST')
            ),
            IGenreRepository.SearchResult(
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
            IGenreRepository.SearchParams(
                init_page=2,
                init_per_page=2,
                init_filter=GenreFilter(name='TEST')
            ),
            IGenreRepository.SearchResult(
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
                                                                  search_params: IGenreRepository.SearchParams,
                                                                  expected_search_output: IGenreRepository.SearchResult):
        categories = Category.fake().the_categories(2).build()
        self.category_repo.bulk_insert(categories)
        genres = [
            Genre.fake().a_genre().add_category_id(
                categories[0].category_id).add_category_id(
                    categories[1].category_id).with_name('test').build(),
            Genre.fake().a_genre().add_category_id(
                categories[0].category_id).add_category_id(
                    categories[1].category_id).with_name('a').build(),
            Genre.fake().a_genre().add_category_id(
                categories[0].category_id).add_category_id(
                    categories[1].category_id).with_name('TEST').build(),
            Genre.fake().a_genre().add_category_id(
                categories[0].category_id).add_category_id(
                    categories[1].category_id).with_name('e').build(),
            Genre.fake().a_genre().add_category_id(
                categories[0].category_id).add_category_id(
                    categories[1].category_id).with_name('TeSt').build(),
        ]
        self.genre_repo.bulk_insert(genres)

        search_result = self.genre_repo.search(search_params)
        expected_search_output.items = [genres[i]  # type: ignore
                                        for i in expected_search_output.items]
        assert search_result == expected_search_output

    @pytest.mark.parametrize('search_params, expected_search_output', [
        pytest.param(
            {
                'init_page': 1,
                'init_per_page': 2,
                'init_sort': 'name',
                'init_filter': {
                    'categories_id': [0],
                }
            },
            {
                'items': [2, 1],
                'total': 3,
                'current_page': 1,
                'per_page': 2,
            },
            id='sort by name asc, filter by categories_id = [0] page = 1'
        ),
        pytest.param(
            {
                'init_page': 2,
                'init_per_page': 2,
                'init_sort': 'name',
                'init_filter': {
                    'categories_id': [0],
                }
            },
            {
                'items': [0],
                'total': 3,
                'current_page': 2,
                'per_page': 2,

            },
            id='sort by name asc, filter by categories_id = [0] page = 2'
        )
    ])
    def test_search_applying_sort_and_paginate_and_filter_by_categories_id(self,
                                                                           search_params: Dict[str, Any],
                                                                           expected_search_output: Dict[str, Any]):
        categories = Category.fake().the_categories(4).build()
        self.category_repo.bulk_insert(categories)
        genres = [
            Genre.fake()
            .a_genre()
            .add_category_id(categories[0].category_id)
            .with_name('test')
            .build(),
            Genre.fake()
            .a_genre()
            .add_category_id(categories[0].category_id)
            .add_category_id(categories[1].category_id)
            .with_name('a')
            .build(),
            Genre.fake()
            .a_genre()
            .add_category_id(categories[0].category_id)
            .add_category_id(categories[1].category_id)
            .add_category_id(categories[2].category_id)
            .with_name('TEST')
            .build(),
            Genre.fake()
            .a_genre()
            .add_category_id(categories[3].category_id)
            .with_name('e')
            .build(),
            Genre.fake()
            .a_genre()
            .add_category_id(categories[1].category_id)
            .add_category_id(categories[2].category_id)
            .with_name('TeSt')
            .build(),
        ]
        self.genre_repo.bulk_insert(genres)

        search_result = self.genre_repo.search(
            IGenreRepository.SearchParams(
                init_page=search_params['init_page'],
                init_per_page=search_params['init_per_page'],
                init_filter=GenreFilter(
                    categories_id={
                        categories[index].category_id
                        for index in search_params['init_filter']['categories_id']
                    }
                ),
            )
        )
        expected_search_output['items'] = [genres[i]  # type: ignore
                                           for i in expected_search_output['items']]
        assert search_result == IGenreRepository.SearchResult(
            **expected_search_output)

    @pytest.mark.parametrize('search_params, expected_search_output', [
        pytest.param(
            {
                'init_page': 1,
                'init_per_page': 2,
                'init_sort': 'name',
                'init_filter': {
                    'name': 'TEST',
                    'categories_id': [1],
                }
            },
            {
                'items': [2, 4],
                'total': 3,
                'current_page': 1,
                'per_page': 2,
            },
            id='sort by name asc, filter by name = TEST, categories_id = [1] page = 1'
        ),
        pytest.param(
            {
                'init_page': 2,
                'init_per_page': 2,
                'init_sort': 'name',
                'init_filter': {
                    'name': 'TEST',
                    'categories_id': [1],
                }
            },
            {
                'items': [0],
                'total': 3,
                'current_page': 2,
                'per_page': 2,
            },
            id='sort by name asc, filter by name = TEST, categories_id = [1] page = 2'
        ),
    ])
    def test_search_applying_sort_and_paginate_and_filter_by_name_and_categories_id(self,
                                                                                    search_params: Dict[str, Any],
                                                                                    expected_search_output: Dict[str, Any]):
        categories = Category.fake().the_categories(4).build()
        self.category_repo.bulk_insert(categories)
        genres = [
            Genre.fake()
            .a_genre()
            .add_category_id(categories[0].category_id)
            .add_category_id(categories[1].category_id)
            .with_name('test')
            .build(),
            Genre.fake()
            .a_genre()
            .add_category_id(categories[0].category_id)
            .add_category_id(categories[1].category_id)
            .with_name('a')
            .build(),
            Genre.fake()
            .a_genre()
            .add_category_id(categories[0].category_id)
            .add_category_id(categories[1].category_id)
            .add_category_id(categories[2].category_id)
            .with_name('TEST')
            .build(),
            Genre.fake()
            .a_genre()
            .add_category_id(categories[3].category_id)
            .with_name('e')
            .build(),
            Genre.fake()
            .a_genre()
            .add_category_id(categories[1].category_id)
            .add_category_id(categories[2].category_id)
            .with_name('TeSt')
            .build(),
        ]
        self.genre_repo.bulk_insert(genres)

        search_result = self.genre_repo.search(
            IGenreRepository.SearchParams(
                init_page=search_params['init_page'],
                init_per_page=search_params['init_per_page'],
                init_filter=GenreFilter(
                    name=search_params['init_filter']['name'],
                    categories_id={
                        categories[index].category_id
                        for index in search_params['init_filter']['categories_id']
                    }
                ),
                init_sort=search_params['init_sort'],
                init_sort_dir=search_params.get('init_sort_dir', 'asc')
            )
        )
        expected_search_output['items'] = [genres[i]  # type: ignore
                                           for i in expected_search_output['items']]
        print(search_result.items, expected_search_output['items'])
        assert search_result == IGenreRepository.SearchResult(
            **expected_search_output)
