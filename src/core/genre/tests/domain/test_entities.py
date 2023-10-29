from datetime import datetime
from typing import Annotated, Any, Dict, List, Set
from core.category.domain.entities import CategoryId
from pydantic import Strict, StrictBool, ValidationError
import pytest
from core.genre.domain.entities import Genre, GenreId
from core.shared.domain.entities import AggregateRoot


class TestGenre:

    def test_should_be_a_aggregate_root_subclass(self):
        assert issubclass(Genre, AggregateRoot)

    def test_should_be_slots(self):
        # python 12
        # assert Genre.__dataclass_params__.slots is True  # pylint: disable=no-member # type: ignore
        assert Genre.__slots__ == (
            'genre_id', 'name', 'categories_id', 'is_active', 'created_at')

    # def test_should_be_kw_only(self):
    #     assert Genre.__dataclass_params__.kw_only is True  # pylint: disable=no-member # type: ignore

    def test_should_generate_a_new_id(self):
        genre = Genre(
            name='Test Genre', categories_id={CategoryId()})
        assert genre.genre_id is not None
        assert isinstance(genre.genre_id, GenreId)

    def test_should_generate_a_new_created_at(self):
        genre = Genre(
            name='Test Genre', categories_id={CategoryId()})
        assert genre.created_at is not None
        assert isinstance(genre.created_at, datetime)

    def test_should_be_equal_to_another_genre_with_the_same_id(self):
        genre_id = GenreId()
        genre1 = Genre(
            genre_id=genre_id, name='Test Genre 1', categories_id={CategoryId()})
        genre2 = Genre(
            genre_id=genre_id, name='Test Genre 1', categories_id={CategoryId()})
        assert genre1.equals(genre2)

    def test_should_not_be_equal_to_another_genre_with_a_different_id(self):
        genre1 = Genre(genre_id=GenreId(
        ), name='Test Genre', categories_id={CategoryId()})
        genre2 = Genre(genre_id=GenreId(
        ), name='Test Genre', categories_id={CategoryId()})
        assert genre1 != genre2

    def test_should_generate_an_error_in_change_name(self):
        genre = Genre(genre_id=GenreId(
        ), name='Test Genre', categories_id={CategoryId()})
        genre.change_name(1)  # type: ignore
        assert genre.notification.has_errors() is True
        assert len(genre.notification.errors) == 1
        assert genre.notification.errors == {
            'name': ['Input should be a valid string']
        }

    def test_should_change_name(self):
        genre = Genre(genre_id=GenreId(
        ), name='Test Genre', categories_id={CategoryId()})
        new_name = 'New Test Genre'
        genre.change_name(new_name)
        assert genre.name == new_name
    
    def test_should_add_a_category_id(self):
        genre = Genre(genre_id=GenreId(
        ), name='Test Genre', categories_id={CategoryId()})
        category_id = CategoryId()
        genre.add_category_id(category_id)
        assert category_id in genre.categories_id

        copy_categories_id = CategoryId(category_id.id)
        genre.add_category_id(copy_categories_id)
        assert len(genre.categories_id) == 2

    def test_should_generate_an_error_in_sync_categories_id(self):
        genre = Genre(genre_id=GenreId(
        ), name='Test Genre', categories_id={CategoryId()})

        genre.sync_categories_id('fake value')
        assert genre.notification.has_errors() is True
        assert len(genre.notification.errors) == 1
        assert genre.notification.errors == {
            'categories_id': ['Input should be a valid set']
        }

        genre.sync_categories_id(set())
        assert genre.notification.has_errors() is True
        assert len(genre.notification.errors) == 1
        assert genre.notification.errors == {
            'categories_id': [
                'Input should be a valid set',
                'Set should have at least 1 item after validation, not 0'
            ]
        }

        genre.sync_categories_id({1})
        assert genre.notification.has_errors() is True
        assert len(genre.notification.errors) == 1
        assert genre.notification.errors == {
            'categories_id': [
                'Input should be a valid set',
                'Set should have at least 1 item after validation, not 0',
                'Input should be a dictionary or an instance of CategoryId'
            ]
        }

    def test_should_activate_category(self):
        genre = Genre(
            genre_id=GenreId(),
            name='Test Category',
            categories_id={CategoryId()},
            is_active=False)
        genre.activate()
        assert genre.is_active is True

    def test_should_deactivate_category(self):
        genre = Genre(
            genre_id=GenreId(),
            name='Test Category',
            categories_id={CategoryId()},
            is_active=True)
        genre.deactivate()
        assert genre.is_active is False

    def test_fields_mapping(self):
        assert Genre.__annotations__ == {
            'genre_id': GenreId,
            'name': str,
            'categories_id': Set[CategoryId],
            'is_active': StrictBool,
            'created_at': Annotated[datetime, Strict()]
        }

    @pytest.mark.parametrize('_input, expected', [
        pytest.param(
            {},
            [
                {
                    'msg': 'Field required',
                    'type': 'missing',
                    'loc': ('name',)
                },
                {
                    'msg': 'Field required',
                    'type': 'missing',
                    'loc': ('categories_id',)
                }
            ],
            id='empty input'
        ),
        pytest.param(
            {
                'name': 1,
                'categories_id': 'fake value',
                'is_active': 'fake value',
                'created_at': 1
            },
            [
                {
                    'msg': 'Input should be a valid string',
                    'type': 'string_type',
                    'loc': ('name',)
                },
                {
                    'msg': 'Input should be a valid set',
                    'type': 'set_type',
                    'loc': ('categories_id',)
                },
                {
                    'msg': 'Input should be a valid boolean',
                    'type': 'bool_type',
                    'loc': ('is_active',)
                },
                {
                    'msg': 'Input should be a valid datetime',
                    'type': 'datetime_type',
                    'loc': ('created_at',)
                }
            ],
            id='all invalid input'
        ),
        pytest.param(
            {
                'name': 't' * 256,
                'categories_id': {CategoryId()}
            },
            [
                {
                    'msg': 'String should have at most 255 characters',
                    'type': 'string_too_long',
                    'loc': ('name',)
                }
            ],
            id='name with more than 255 characters'
        ),
        pytest.param(
            {
                'name': 't',
                'categories_id': {}
            },
            [
                {
                    'msg': 'Input should be a valid set',
                    'type': 'set_type',
                    'loc': ('categories_id',)
                }
            ],
            id='categories_id with 0 items'
        ),
        pytest.param(
            {
                'name': 't',
                'categories_id': {1}
            },
            [
                {
                    'msg': 'Input should be a dictionary or an instance of CategoryId',
                    'type': 'dataclass_type',
                    'loc': ('categories_id',0)
                }
            ],
            id='categories_id with 1 invalid item'
        )
    ])
    def test_should_throw_an_validation_error_on_constructor(self,
                                                             _input: Dict[str, Any],
                                                             expected: List[Dict[str, Any]]):
        with pytest.raises(ValidationError) as e:
            Genre(**_input)
        assert len(e.value.errors()) == len(expected)

        # sourcery skip: no-loop-in-tests
        for index, error in enumerate(e.value.errors()):
            assert error['msg'] == expected[index]['msg']
            assert error['type'] == expected[index]['type']
            assert error['loc'] == expected[index]['loc']
