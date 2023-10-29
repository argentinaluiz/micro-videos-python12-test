
from datetime import datetime
from core.category.domain.entities import CategoryId
from core.genre.domain.entities import Genre, GenreId

from core.genre.domain.entities_fake_builder import GenreFakerBuilder
import pytest


class TestGenreFakeBuilder:

    def test_genre_id_prop_throw_exception_when_is_none(self):
        with pytest.raises(ValueError) as assert_exception:
            faker = GenreFakerBuilder.a_genre()
            faker.genre_id  # pylint: disable=pointless-statement
        assert str(
            assert_exception.value) == 'Prop genre_id not have a factory, use "with methods"'

    def test_genre_id_prop(self):
        faker = GenreFakerBuilder.a_genre()
        genre_id = GenreId()
        this = faker.with_genre_id(genre_id)

        assert isinstance(this, GenreFakerBuilder)
        assert faker.genre_id == genre_id

    def test_invalid_cases_for_name_prop(self):
        faker = GenreFakerBuilder.a_genre()

        name_value = faker.with_invalid_name_too_long().name
        assert len(name_value) == 256

    def test_name_prop(self):
        faker = GenreFakerBuilder.a_genre()
        assert isinstance(faker.name, str)

        this = faker.with_name('name test')
        assert isinstance(this, GenreFakerBuilder)
        assert faker.name == 'name test'

    def test_categories_id_prop(self):
        faker = GenreFakerBuilder.a_genre()
        assert len(faker.categories_id) == 1

        category_id = CategoryId()
        this = faker.add_category_id(category_id)
        assert isinstance(this, GenreFakerBuilder)
        assert len(faker.categories_id) == 1
        assert category_id in faker.categories_id

    def test_created_at_prop_throw_exception_when_is_none(self):
        with pytest.raises(Exception) as assert_exception:
            faker = GenreFakerBuilder.a_genre()
            faker.created_at  # pylint: disable=pointless-statement
        assert str(
            assert_exception.value) == 'Prop created_at not have a factory, use "with methods"'

    def test_created_at_prop(self):
        faker = GenreFakerBuilder.a_genre()
        date = datetime.now()
        this = faker.with_created_at(date)

        assert isinstance(this, GenreFakerBuilder)
        assert faker.created_at == date

    def test_build_a_genre(self):
        faker = GenreFakerBuilder.a_genre()
        genre = faker.build()

        self.assert_props_types(genre)

        genre_id = GenreId()
        category_id = CategoryId()
        date = datetime.now()
        builder = faker.with_genre_id(genre_id)\
            .with_name('name test')\
            .add_category_id(category_id)\
            .with_created_at(date)

        genre = builder.build()
        assert genre is not None
        self.assert_genre(
            genre, genre_id, date, category_id)

    def test_build_the_genres(self):
        faker = GenreFakerBuilder.the_genres(2)
        genres = faker.build()

        assert genres is not None
        assert isinstance(genres, list)
        assert len(genres) == 2

        for genre in genres:  # sourcery skip: no-loop-in-tests
            self.assert_props_types(genre)

        genre_id = GenreId()
        category_id = CategoryId()
        date = datetime.now()
        builder = faker.with_genre_id(genre_id)\
            .with_name('name test')\
            .add_category_id(category_id)\
            .with_created_at(date)

        genres = builder.build()

        for genre in genres:
            self.assert_genre(
                genre, genre_id, date, category_id)

    def assert_props_types(self, genre: Genre):
        assert genre is not None
        assert isinstance(genre.genre_id, GenreId)
        assert isinstance(genre.name, str)
        assert isinstance(genre.categories_id, set)
        assert len(genre.categories_id) >= 1
        assert isinstance(genre.created_at, datetime)

    def assert_genre(self,
                     genre: Genre,
                     genre_id: GenreId,
                     created_at: datetime,
                     category_id: CategoryId):
        assert genre.genre_id == genre_id
        assert genre.name == 'name test'
        assert category_id in genre.categories_id
        assert genre.created_at == created_at
