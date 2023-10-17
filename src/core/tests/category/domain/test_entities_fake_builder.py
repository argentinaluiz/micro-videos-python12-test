
from datetime import datetime
from core.category.domain.entities import Category

from core.category.domain.entities_fake_builder import CategoryFakerBuilder
from core.shared.domain.value_objects import Uuid
import pytest

class TestCategoryFakeBuilder:

    def test_category_id_prop_throw_exception_when_is_none(self):
        with pytest.raises(ValueError) as assert_exception:
            faker = CategoryFakerBuilder.a_category()
            faker.category_id # pylint: disable=pointless-statement
        assert str(assert_exception.value) == 'Prop category_id not have a factory, use "with methods"'

    def test_category_id_prop(self):
        faker = CategoryFakerBuilder.a_category()
        category_id = Uuid()
        this = faker.with_category_id(category_id)

        assert isinstance(this, CategoryFakerBuilder)
        assert faker.category_id == category_id

    def test_invalid_cases_for_name_prop(self):
        faker = CategoryFakerBuilder.a_category()

        name_value = faker.with_invalid_name_too_long().name
        assert len(name_value) == 256

    def test_name_prop(self):
        faker = CategoryFakerBuilder.a_category()
        assert isinstance(faker.name, str)

        this = faker.with_name('name test')
        assert isinstance(this, CategoryFakerBuilder)
        assert faker.name == 'name test'

    def test_description_prop(self):
        faker = CategoryFakerBuilder.a_category()
        assert isinstance(faker.description, str)

        this = faker.with_description('description test')
        assert isinstance(this, CategoryFakerBuilder)
        assert faker.description == 'description test'

    def test_is_active_prop(self):
        faker = CategoryFakerBuilder.a_category()
        assert isinstance(faker.is_active, bool)

        this = faker.deactivate()
        assert isinstance(this, CategoryFakerBuilder)
        assert not faker.is_active

        this = faker.activate()
        assert isinstance(this, CategoryFakerBuilder)
        assert faker.is_active

    def test_created_at_prop_throw_exception_when_is_none(self):
        with pytest.raises(Exception) as assert_exception:
            faker = CategoryFakerBuilder.a_category()
            faker.created_at # pylint: disable=pointless-statement
        assert str(assert_exception.value) == 'Prop created_at not have a factory, use "with methods"'

    def test_created_at_prop(self):
        faker = CategoryFakerBuilder.a_category()
        date = datetime.now()
        this = faker.with_created_at(date)

        assert isinstance(this, CategoryFakerBuilder)
        assert faker.created_at == date

    def test_build_a_category(self):
        faker = CategoryFakerBuilder.a_category()
        category = faker.build()

        self.assert_props_types(category)

        category_id = Uuid()
        date = datetime.now()
        builder = faker.with_category_id(category_id)\
            .with_name('name test')\
            .with_description('description test')\
            .deactivate()\
            .with_created_at(date)

        category = builder.build()
        assert category is not None
        self.assert_category(category, category_id, date)

        category = builder.activate().build()
        assert category is not None

    def test_build_the_categories(self):
        faker = CategoryFakerBuilder.the_categories(2)
        categories = faker.build()

        assert categories is not None
        assert isinstance(categories, list)
        assert len(categories) == 2

        for category in categories: # sourcery skip: no-loop-in-tests
            self.assert_props_types(category)

        category_id = Uuid()
        date = datetime.now()
        # pylint: disable=no-member
        builder = faker.with_category_id(category_id)\
            .with_name('name test')\
            .with_description('description test')\
            .deactivate()\
            .with_created_at(date)

        categories = builder.build()

        for category in categories:
            self.assert_category(category, category_id, date)

        categories = builder.activate().build()
        for category in categories:
            assert category is not None

    def assert_props_types(self, category: Category):
        assert category is not None
        assert isinstance(category.category_id, Uuid)
        assert isinstance(category.name, str)
        assert isinstance(category.description, str)
        assert isinstance(category.is_active, bool)
        assert isinstance(category.created_at, datetime)

    def assert_category(self, category: Category, category_id: Uuid, created_at: datetime):
        assert category.category_id == category_id
        assert category.name == 'name test'
        assert category.description == 'description test'
        assert not category.is_active
        assert category.created_at == created_at
