from core.category.domain.entities import CategoryId
from core.genre.domain.repositories import GenreFilter
from pydantic import ValidationError
import pytest


class TestGenreFilter:

    def test_invalidation(self):
        with pytest.raises(ValidationError) as ex:
            GenreFilter(name='a', categories_id={})
        assert ex.value.errors()[0]['loc'] == ('categories_id',)
        assert ex.value.errors()[0]['msg'] == 'Input should be a valid set'
        assert ex.value.errors()[0]['type'] == 'set_type'

        with pytest.raises(ValidationError) as ex:
            GenreFilter(name='a', categories_id={1})
        assert ex.value.errors()[0]['loc'] == ('categories_id',0)
        assert ex.value.errors()[0]['msg'] == 'Value error, ID 1 must be a valid UUID'
        assert ex.value.errors()[0]['type'] == 'value_error'

    def test_constructor(self):
        genre_filter = GenreFilter(name='a', categories_id={'6f8a2d1e-0b7e-4b1e-8d5b-0e0c5b9b6b4a'})
        assert genre_filter.name == 'a'
        assert list(genre_filter.categories_id)[0] == CategoryId('6f8a2d1e-0b7e-4b1e-8d5b-0e0c5b9b6b4a')

        category_id = CategoryId()
        genre_filter = GenreFilter(name='a', categories_id={category_id})
        assert genre_filter.name == 'a'
        assert list(genre_filter.categories_id)[0] == category_id