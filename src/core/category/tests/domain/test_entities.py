from datetime import datetime
from typing import Annotated, Any, Dict, List
from pydantic import Strict, StrictBool, ValidationError
import pytest
from core.category.domain.entities import Category
from core.shared.domain.entities import Entity
from core.shared.domain.value_objects import Uuid


class TestCategory:

    def test_should_be_a_entity_subclass(self):
        assert issubclass(Category, Entity)

    def test_should_be_slots(self):
        # python 12
        # assert Category.__dataclass_params__.slots is True  # pylint: disable=no-member # type: ignore
        assert Category.__slots__ == (
            'category_id', 'name', 'description', 'is_active', 'created_at')

    # def test_should_be_kw_only(self):
    #     assert Category.__dataclass_params__.kw_only is True  # pylint: disable=no-member # type: ignore

    def test_should_generate_a_new_id(self):
        category = Category(name='Test Category')
        assert category.category_id is not None
        assert isinstance(category.category_id, Uuid)

    def test_should_generate_a_new_created_at(self):
        category = Category(name='Test Category')
        assert category.created_at is not None
        assert isinstance(category.created_at, datetime)

    def test_should_be_equal_to_another_category_with_the_same_id(self):
        category_id = Uuid()
        category1 = Category(category_id=category_id, name='Test Category 1')
        category2 = Category(category_id=category_id, name='Test Category 1')
        assert category1.equals(category2)

    def test_should_not_be_equal_to_another_category_with_a_different_id(self):
        category1 = Category(category_id=Uuid(), name='Test Category')
        category2 = Category(category_id=Uuid(), name='Test Category')
        assert category1 != category2

    def test_should_generate_an_error_in_change_name(self):
        category = Category(category_id=Uuid(), name='Test Category')
        category.change_name(1)  # type: ignore
        assert category.notification.has_errors() is True
        assert len(category.notification.errors) == 1
        assert category.notification.errors == {
            'name': ['Input should be a valid string']
        }

    def test_should_change_name(self):
        category = Category(category_id=Uuid(), name='Test Category')
        new_name = 'New Test Category'
        category.change_name(new_name)
        assert category.name == new_name

    def test_should_change_description(self):
        category = Category(category_id=Uuid(), name='Test Category')
        new_description = 'New Test Description'
        category.change_description(new_description)
        assert category.description == new_description

    def test_should_generate_an_error_in_change_description(self):
        category = Category(category_id=Uuid(), name='Test Category')
        category.change_description(1)  # type: ignore
        assert category.notification.has_errors() is True
        assert len(category.notification.errors) == 1
        assert category.notification.errors == {
            'description': ['Input should be a valid string']
        }

    def test_should_activate_category(self):
        category = Category(category_id=Uuid(),
                            name='Test Category', is_active=False)
        category.activate()
        assert category.is_active is True

    def test_should_deactivate_category(self):
        category = Category(category_id=Uuid(),
                            name='Test Category', is_active=True)
        category.deactivate()
        assert category.is_active is False

    def test_fields_mapping(self):
        assert Category.__annotations__ == {
            'category_id': Uuid,
            'name': str,
            'description': str | None,
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
                }
            ],
            id='empty input'
        ),
        pytest.param(
            {
                'name': 1,
                'description': 1,
                'is_active': 'a',
                'created_at': 1
            },
            [
                {
                    'msg': 'Input should be a valid string',
                    'type': 'string_type',
                    'loc': ('name',)
                },
                {
                    'msg': 'Input should be a valid string',
                    'type': 'string_type',
                    'loc': ('description',)
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
            },
            [
                {
                    'msg': 'String should have at most 255 characters',
                    'type': 'string_too_long',
                    'loc': ('name',)
                }
            ],
            id='name with more than 255 characters'
        )
    ])
    def test_should_throw_an_validation_error_on_constructor(self,
                                                             _input: Dict[str, Any],
                                                             expected: List[Dict[str, Any]]):
        with pytest.raises(ValidationError) as e:
            Category(**_input)
        assert len(e.value.errors()) == len(expected)

        # sourcery skip: no-loop-in-tests
        for index, error in enumerate(e.value.errors()):
            assert error['msg'] == expected[index]['msg']
            assert error['type'] == expected[index]['type']
            assert error['loc'] == expected[index]['loc']
