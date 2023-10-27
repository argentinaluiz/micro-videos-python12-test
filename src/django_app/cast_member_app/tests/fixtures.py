from collections import namedtuple
import datetime
from typing import Any, Dict, NamedTuple, TypedDict
from core.shared.domain.exceptions import EntityValidationException
from pydantic import ValidationError
from pydantic.errors import Literal
from pydantic_core import InitErrorDetails
import pytest
from core.cast_member.domain.entities import CastMember


class CreateCastMemberApiFixture:

    @staticmethod
    def keys_in_response():
        return ['id', 'name', 'type', 'created_at']

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
                        ),
                        InitErrorDetails(
                            loc=('type',),
                            type='missing',
                            input=None
                        )
                    ]
                )
            ),
            ArrangeDict(
                id='name_none',
                request_body={
                    'name': None,
                    'type': CastMember.DIRECTOR
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
                    'name': '',
                    'type': CastMember.DIRECTOR
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
                    'name': 5,
                    'type': CastMember.DIRECTOR
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
                id='type_invalid',
                request_body={
                    'name': 'cast member test',
                    'type': 'a'
                },
                exception=ValidationError.from_exception_data(
                    title='',
                    line_errors=[
                        InitErrorDetails(
                            loc=('type',),
                            type='literal_error',
                            input=None,
                            ctx={'expected': '1 or 2'}
                        )
                    ]
                )
            ),
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
                    'name': 't' * 256,
                    'type': CastMember.DIRECTOR
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
        faker = CastMember.fake()\
            .a_director()\
            .with_name('cast member test')
        arrange = (
            {
                'request_body': {'name': faker.name, 'type': faker.type},
                'response_body': {
                    'name': faker.name,
                    'type': faker.type,
                }
            },
            {
                'request_body': {
                    'name': faker.name,
                    'type': CastMember.ACTOR
                },
                'response_body': {
                    'name': faker.name,
                    'type': CastMember.ACTOR,
                }
            },
        )
        return (pytest.param(item['request_body'], item['response_body'], id=str(item['request_body'])) for item in arrange)


class UpdateCastMemberApiFixture:

    @staticmethod
    def keys_in_response():
        return ['id', 'name', 'type', 'created_at']

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
                id='type_invalid',
                request_body={
                    'name': 'cast member test',
                    'type': 'a'
                },
                exception=ValidationError.from_exception_data(
                    title='',
                    line_errors=[
                        InitErrorDetails(
                            loc=('type',),
                            type='literal_error',
                            input=None,
                            ctx={'expected': '1 or 2'}
                        )
                    ]
                )
            ),
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
                    'name': 't' * 256,
                    'type': CastMember.DIRECTOR
                },
                exception=EntityValidationException({
                    'name': ['String should have at most 255 characters']
                })
            ),
        )
        return (pytest.param(item['request_body'], item['exception'], id=item['id']) for item in arrange)

    @staticmethod
    def arrange_for_update():
        faker = CastMember.fake()\
            .a_director()\
            .with_name('cast member test')
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
                    'type': CastMember.ACTOR
                },
                'response_body': {
                    'name': faker.name,
                    'type': CastMember.ACTOR,
                },
                'entity': faker.build(),
            },
            {
                'request_body': {
                    'type': CastMember.ACTOR
                },
                'response_body': {
                    'type': CastMember.ACTOR,
                },
                'entity': faker.build(),
            },
        )
        return (pytest.param(item['request_body'], item['response_body'], item['entity'], id=str(item['request_body'])) for item in arrange)


class GetObjectCastMemberApiFixture:

    @staticmethod
    def keys_in_cast_member_response():
        return ['id', 'name', 'type', 'created_at']


class ListCastMembersApiFixture:

    @staticmethod
    def arrange_incremented_with_created_at():
        cast_members = CastMember.fake()\
            .the_cast_members(4)\
            .with_created_at(
            lambda self, index: datetime.datetime.now(
                datetime.timezone.utc) + datetime.timedelta(days=index)
        )\
            .build()

        class CastMembersNamed(NamedTuple):
            first: CastMember
            second: CastMember
            third: CastMember
            fourth: CastMember

        categories_named = CastMembersNamed(
            first=cast_members[0],
            second=cast_members[1],
            third=cast_members[2],
            fourth=cast_members[3],
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
                'entities': cast_members
            },
            {
                'request_query_params': {'page': 1, 'per_page': 2},
                'expected_entities': (
                    categories_named.fourth,
                    categories_named.third
                ),
                'expected_meta': {'total': 4, 'current_page': 1, 'per_page': 2, 'last_page': 2},
                'entities': cast_members
            },
            {
                'request_query_params': {'page': 2, 'per_page': 2},
                'expected_entities': (
                    categories_named.second,
                    categories_named.first
                ),
                'expected_meta': {'total': 4, 'current_page': 2, 'per_page': 2, 'last_page': 2},
                'entities': cast_members
            }
        )

        return [pytest.param(
            item['request_query_params'],
            item['expected_entities'],
            item['expected_meta'],
            item['entities'],
            id=f'query_params={str(item["request_query_params"])}') for item in arrange]

    @staticmethod
    def arrange_unsorted():
        actor = CastMember.fake().an_actor()
        director = CastMember.fake().a_director()
        created_at = datetime.datetime.now(datetime.timezone.utc)
        CastMembersNamed = namedtuple(
            'CastMembersNamed', [
                'actor_a', 'actor_AAA', 'actor_AaA', 'actor_b', 'actor_c', 'director_f', 'director_e'
            ])
        cast_members_named = CastMembersNamed(
            actor_a=actor
                .with_name('a')
                .with_created_at(created_at + datetime.timedelta(days=1))
                .build(),
            actor_AAA=actor
                .with_name('AAA')
                .with_created_at(created_at + datetime.timedelta(days=2))
                .build(),
            actor_AaA=actor
                .with_name('AaA')
                .with_created_at(created_at + datetime.timedelta(days=3))
                .build(),
            actor_b=actor
                .with_name('b')
                .with_created_at(created_at + datetime.timedelta(days=4))
                .build(),
            actor_c=actor
                .with_name('c')
                .with_created_at(created_at + datetime.timedelta(days=5))
                .build(),
            director_f=director
                .with_name('f')
                .with_created_at(created_at + datetime.timedelta(days=6))
                .build(),
            director_e=director
                .with_name('e')
                .with_created_at(created_at + datetime.timedelta(days=7))
                .build()
        )
        cast_members = list(cast_members_named)

        arrange = (
            {
                'request_query_params': {
                    'page': 1,
                    'per_page': 2,
                    'sort': 'name',
                    'filter': {'name': 'a'}
                },
                'expected_entities': (
                    cast_members_named.actor_AAA,
                    cast_members_named.actor_AaA,
                ),
                'expected_meta': {'total': 3, 'current_page': 1, 'per_page': 2, 'last_page': 2},
                'entities': cast_members
            },
            {
                'request_query_params': {
                    'page': 2,
                    'per_page': 2,
                    'sort': 'name',
                    'filter': {'name': 'a'}
                },
                'expected_entities': (
                    cast_members_named.actor_a,
                ),
                'expected_meta': {'total': 3, 'current_page': 2, 'per_page': 2, 'last_page': 2},
                'entities': cast_members
            },
        )

        return [pytest.param(
            item['request_query_params'],
            item['expected_entities'],
            item['expected_meta'],
            item['entities'],
            id=f'query_params={str(item["request_query_params"])}') for item in arrange]
