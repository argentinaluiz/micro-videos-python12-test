from collections import namedtuple
import datetime
from typing import Any, Dict, NamedTuple, TypedDict
from core.shared.domain.exceptions import EntityValidationException
from pydantic import ValidationError
from pydantic_core import InitErrorDetails
import pytest
from core.category.domain.entities import Category


class CreateCategoryApiFixture:

    @staticmethod
    def keys_in_response():
        return ['id', 'name', 'description', 'is_active', 'created_at']

    @staticmethod
    def arrange_for_invalid_requests():
        ArrangeDict = TypedDict('arrange_dict', {
            'id': str,
            'request_body': Dict[str, Any],
            'exception': ValidationError
        })
        arrange = (
            ArrangeDict(
                id='body_empty',
                request_body={},
                exception=ValidationError.from_exception_data(
                    title='',
                    line_errors=[
                        InitErrorDetails(
                            loc=('name',),
                            type='missing',
                            input=None
                        )
                    ]
                )
            ),
            ArrangeDict(
                id='name_none',
                request_body={
                    'name': None
                },
                exception=ValidationError.from_exception_data(
                    title='',
                    line_errors=[
                        InitErrorDetails(
                            loc=('name',),
                            type='string_type',
                            input=None
                        )
                    ]
                )
            ),
            ArrangeDict(
                id='name_empty',
                request_body={
                    'name': ''
                },
                exception=ValidationError.from_exception_data(
                    title='',
                    line_errors=[
                        InitErrorDetails(
                            loc=('name',),
                            type='string_type',
                            input=None
                        )
                    ]
                )
            ),
            ArrangeDict(
                id='name_not_a_str',
                request_body={
                    'name': 5
                },
                exception=ValidationError.from_exception_data(
                    title='',
                    line_errors=[
                        InitErrorDetails(
                            loc=('name',),
                            type='string_type',
                            input=None
                        )
                    ]
                )
            ),
            ArrangeDict(
                id='description_not_a_str',
                request_body={
                    'description': 5
                },
                exception=ValidationError.from_exception_data(
                    title='',
                    line_errors=[
                        InitErrorDetails(
                            loc=('name',),
                            type='missing',
                            input=None
                        ),
                        InitErrorDetails(
                            loc=('description',),
                            type='string_type',
                            input=None
                        )
                    ]
                )
            ),
            ArrangeDict(
                id='is_active_none',
                request_body={
                    'is_active': None
                },
                exception=ValidationError.from_exception_data(
                    title='',
                    line_errors=[
                        InitErrorDetails(
                            loc=('name',),
                            type='missing',
                            input=None
                        ),
                        InitErrorDetails(
                            loc=('is_active',),
                            type='bool_type',
                            input=None
                        )
                    ]
                )
            ),
            ArrangeDict(
                id='is_active_not_bool',
                request_body={
                    'is_active': 1
                },
                exception=ValidationError.from_exception_data(
                    title='',
                    line_errors=[
                        InitErrorDetails(
                            loc=('name',),
                            type='missing',
                            input=None
                        ),
                        InitErrorDetails(
                            loc=('is_active',),
                            type='bool_type',
                            input=None
                        )
                    ]
                )
            )
        )
        return (pytest.param(item['request_body'], item['exception'], id=item['id']) for item in arrange)

    @staticmethod
    def arrange_for_entity_validation_error():
        ArrangeDict = TypedDict('arrange_dict', {
            'id': str,
            'request_body': Dict[str, Any],
            'exception': ValidationError
        })
        arrange = (
            ArrangeDict(
                id='name_too_long',
                request_body={
                    'name': 't' * 256
                },
                exception=ValidationError.from_exception_data(
                    title='',
                    line_errors=[
                        InitErrorDetails(
                            loc=('name',),
                            type='string_too_long',
                            input=None,
                            ctx={'max_length': 255}
                        )
                    ]
                )
            ),
        )
        return (pytest.param(item['request_body'], item['exception'], id=item['id']) for item in arrange)

    @staticmethod
    def arrange_for_create():
        faker = Category.fake()\
            .a_category()\
            .with_name('Movie')\
            .with_description('description test')
        arrange = (
            {
                'request_body': {'name': faker.name},
                'response_body': {
                    'name': faker.name,
                    'description': None,
                    'is_active': True,
                }
            },
            {
                'request_body': {
                    'name': faker.name,
                    'description': faker.description,
                },
                'response_body': {
                    'name': faker.name,
                    'description': faker.description,
                    'is_active': True,
                }
            },
            {
                'request_body': {
                    'name': faker.name,
                    'is_active': True
                },
                'response_body': {
                    'name': faker.name,
                    'description': None,
                    'is_active': True,
                }
            },
            {
                'request_body': {
                    'name': faker.name,
                    'is_active': False
                },
                'response_body': {
                    'name': faker.name,
                    'description': None,
                    'is_active': False,
                }
            }
        )
        return (pytest.param(item['request_body'], item['response_body'], id=str(item['request_body'])) for item in arrange)


class UpdateCategoryApiFixture:

    @staticmethod
    def keys_in_response():
        return ['id', 'name', 'description', 'is_active', 'created_at']

    @staticmethod
    def arrange_for_invalid_requests():
        ArrangeDict = TypedDict('arrange_dict', {
            'id': str,
            'request_body': Dict[str, Any],
            'exception': ValidationError
        })
        arrange = (
            ArrangeDict(
                id='name_not_a_str',
                request_body={
                    'name': 5
                },
                exception=ValidationError.from_exception_data(
                    title='',
                    line_errors=[
                        InitErrorDetails(
                            loc=('name',),
                            type='string_type',
                            input=None
                        )
                    ]
                )
            ),
            ArrangeDict(
                id='description_not_a_str',
                request_body={
                    'description': 5
                },
                exception=ValidationError.from_exception_data(
                    title='',
                    line_errors=[
                        InitErrorDetails(
                            loc=('description',),
                            type='string_type',
                            input=None
                        )
                    ]
                )
            ),
            ArrangeDict(
                id='is_active_not_bool',
                request_body={
                    'is_active': 1
                },
                exception=ValidationError.from_exception_data(
                    title='',
                    line_errors=[
                        InitErrorDetails(
                            loc=('is_active',),
                            type='bool_type',
                            input=None
                        )
                    ]
                )
            )
        )
        return (pytest.param(item['request_body'], item['exception'], id=item['id']) for item in arrange)

    @staticmethod
    def arrange_for_entity_validation_error():
        ArrangeDict = TypedDict('arrange_dict', {
            'id': str,
            'request_body': Dict[str, Any],
            'exception': EntityValidationException
        })
        arrange = (
            ArrangeDict(
                id='name_too_long',
                request_body={
                    'name': 't' * 256
                },
                exception=EntityValidationException([
                    ValidationError.from_exception_data(
                        title='',
                        line_errors=[
                            InitErrorDetails(
                                loc=('name',),
                                type='string_too_long',
                                input=None,
                                ctx={'max_length': 255}
                            )
                        ]
                    )])
            ),
        )
        return (pytest.param(item['request_body'], item['exception'], id=item['id']) for item in arrange)

    @staticmethod
    def arrange_for_update():
        faker = Category.fake()\
        .a_category()\
        .with_name('Movie')\
        .with_description('description test')
        arrange = (
            {
                'request_body': {'name': faker.name},
                'response_body': {
                    'name': faker.name,
                },
                'entity': faker.build(),
            },
            {
                'request_body': {
                    'name': faker.name,
                    'description': faker.description,
                },
                'response_body': {
                    'name': faker.name,
                    'description': faker.description,
                    'is_active': True,
                },
                'entity': faker.build(),
            },
            {
                'request_body': {
                    'name': faker.name,
                    'is_active': True
                },
                'response_body': {
                    'name': faker.name,
                    'is_active': True,
                },
                'entity': faker.build(),
            },
            {
                'request_body': {
                    'name': faker.name,
                    'is_active': False
                },
                'response_body': {
                    'name': faker.name,
                    'is_active': False,
                },
                'entity': faker.build(),
            },
            {
                'request_body': {
                    'description': None
                },
                'response_body': {
                    'description': None,
                },
                'entity': faker.build(),
            }
        )
        return (pytest.param(item['request_body'], item['response_body'], item['entity'], id=str(item['request_body'])) for item in arrange)


class GetObjectCategoryApiFixture:

    @ staticmethod
    def keys_in_category_response():
        return ['id', 'name', 'description', 'is_active', 'created_at']


class ListCategoriesApiFixture:

    @ staticmethod
    def arrange_incremented_with_created_at():
        categories = Category.fake()\
        .the_categories(4)\
        .with_created_at(
            lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=index)
        )\
        .build()

        class CategoriesNamed(NamedTuple):
            first: Category
            second: Category
            third: Category
            fourth: Category

        categories_named = CategoriesNamed(
            first=categories[0],
            second=categories[1],
            third=categories[2],
            fourth=categories[3],
        )

        arrange = (
            {
                'request_query_params': {},
                'expected_entities': (
                    categories_named.fourth,
                    categories_named.third,
                    categories_named.second,
                    categories_named.first
                ),
                'expected_meta': {'total': 4, 'current_page': 1, 'per_page': 15, 'last_page': 1},
                'entities': categories
            },
            {
                'request_query_params': {'page': 1, 'per_page': 2},
                'expected_entities': (
                    categories_named.fourth,
                    categories_named.third
                ),
                'expected_meta': {'total': 4, 'current_page': 1, 'per_page': 2, 'last_page': 2},
                'entities': categories
            },
            {
                'request_query_params': {'page': 2, 'per_page': 2},
                'expected_entities': (
                    categories_named.second,
                    categories_named.first
                ),
                'expected_meta': {'total': 4, 'current_page': 2, 'per_page': 2, 'last_page': 2},
                'entities': categories
            }
        )

        return [pytest.param(
            item['request_query_params'],
            item['expected_entities'],
            item['expected_meta'],
            item['entities'],
            id=f'query_params={str(item["request_query_params"])}') for item in arrange]

    @ staticmethod
    def arrange_unsorted():
        faker = Category.fake().a_category()
        categories = [
            faker.with_name('a').build(),
            faker.with_name('AAA').build(),
            faker.with_name('AaA').build(),
            faker.with_name('b').build(),
            faker.with_name('c').build(),
        ]

        class CategoriesNamed(NamedTuple):
            a: Category
            AAA: Category
            AaA: Category
            b: Category
            c: Category

        categories_named = CategoriesNamed(
            a=categories[0],
            AAA=categories[1],
            AaA=categories[2],
            b=categories[3],
            c=categories[4],
        )

        arrange = (
            {
                'request_query_params': {
                    'page': 1,
                    'per_page': 2,
                    'sort': 'name',
                    'filter': 'a'
                },
                'expected_entities': (
                    categories_named.AAA,
                    categories_named.AaA
                ),
                'expected_meta': {'total': 3, 'current_page': 1, 'per_page': 2, 'last_page': 2},
                'entities': categories
            },
            {
                'request_query_params': {
                    'page': 2,
                    'per_page': 2,
                    'sort': 'name',
                    'filter': 'a'
                },
                'expected_entities': (
                    categories_named.a,
                ),
                'expected_meta': {'total': 3, 'current_page': 2, 'per_page': 2, 'last_page': 2},
                'entities': categories
            },
        )

        return [pytest.param(
            item['request_query_params'],
            item['expected_entities'],
            item['expected_meta'],
            item['entities'],
            id=f'query_params={str(item["request_query_params"])}') for item in arrange]
