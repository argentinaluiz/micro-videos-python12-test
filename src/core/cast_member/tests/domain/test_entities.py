from datetime import datetime
from typing import Annotated, Any, Dict, List
from pydantic import Strict, ValidationError
import pytest
from core.cast_member.domain.entities import CastMember, CastMemberId, CastMemberType
from core.shared.domain.entities import AggregateRoot


class TestCastMember:

    def test_should_be_a_aggregate_root_subclass(self):
        assert issubclass(CastMember, AggregateRoot)

    def test_should_be_slots(self):
        # python 12
        # assert CastMember.__dataclass_params__.slots is True  # pylint: disable=no-member # type: ignore
        assert CastMember.__slots__ == (
            'cast_member_id', 'name', 'type', 'created_at')

    # def test_should_be_kw_only(self):
    #     assert CastMember.__dataclass_params__.kw_only is True  # pylint: disable=no-member # type: ignore

    def test_should_generate_a_new_id(self):
        cast_member = CastMember(
            name='Test CastMember', type=CastMember.DIRECTOR)
        assert cast_member.cast_member_id is not None
        assert isinstance(cast_member.cast_member_id, CastMemberId)

    def test_should_generate_a_new_created_at(self):
        cast_member = CastMember(
            name='Test CastMember', type=CastMember.DIRECTOR)
        assert cast_member.created_at is not None
        assert isinstance(cast_member.created_at, datetime)

    def test_should_be_equal_to_another_cast_member_with_the_same_id(self):
        cast_member_id = CastMemberId()
        cast_member1 = CastMember(
            cast_member_id=cast_member_id, name='Test CastMember 1', type=CastMember.DIRECTOR)
        cast_member2 = CastMember(
            cast_member_id=cast_member_id, name='Test CastMember 1', type=CastMember.ACTOR)
        assert cast_member1.equals(cast_member2)

    def test_should_not_be_equal_to_another_cast_member_with_a_different_id(self):
        cast_member1 = CastMember(cast_member_id=CastMemberId(
        ), name='Test CastMember', type=CastMember.DIRECTOR)
        cast_member2 = CastMember(cast_member_id=CastMemberId(
        ), name='Test CastMember', type=CastMember.DIRECTOR)
        assert cast_member1 != cast_member2

    def test_should_generate_an_error_in_change_name(self):
        cast_member = CastMember(cast_member_id=CastMemberId(
        ), name='Test CastMember', type=CastMember.DIRECTOR)
        cast_member.change_name(1)  # type: ignore
        assert cast_member.notification.has_errors() is True
        assert len(cast_member.notification.errors) == 1
        assert cast_member.notification.errors == {
            'name': ['Input should be a valid string']
        }

    def test_should_change_name(self):
        cast_member = CastMember(cast_member_id=CastMemberId(
        ), name='Test CastMember', type=CastMember.DIRECTOR)
        new_name = 'New Test CastMember'
        cast_member.change_name(new_name)
        assert cast_member.name == new_name

    def test_should_generate_an_error_in_change_type(self):
        cast_member = CastMember(cast_member_id=CastMemberId(
        ), name='Test CastMember', type=CastMember.DIRECTOR)
        cast_member.change_type('fake value')
        assert cast_member.notification.has_errors() is True
        assert len(cast_member.notification.errors) == 1
        assert cast_member.notification.errors == {
            'type': ['Input should be 1 or 2']
        }

    def test_should_change_type(self):
        cast_member = CastMember(cast_member_id=CastMemberId(
        ), name='Test CastMember', type=CastMember.DIRECTOR)
        cast_member.change_type(CastMember.ACTOR)
        assert cast_member.type == CastMember.ACTOR

    def test_fields_mapping(self):
        assert CastMember.__annotations__ == {
            'cast_member_id': CastMemberId,
            'name': str,
            'type': CastMemberType,
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
                    'loc': ('type',)
                }
            ],
            id='empty input'
        ),
        pytest.param(
            {
                'name': 1,
                'type': 'fake value',
                'created_at': 1
            },
            [
                {
                    'msg': 'Input should be a valid string',
                    'type': 'string_type',
                    'loc': ('name',)
                },
                {
                    'msg': 'Input should be 1 or 2',
                    'type': 'literal_error',
                    'loc': ('type',)
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
                'type': CastMember.DIRECTOR
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
            CastMember(**_input)
        assert len(e.value.errors()) == len(expected)

        # sourcery skip: no-loop-in-tests
        for index, error in enumerate(e.value.errors()):
            assert error['msg'] == expected[index]['msg']
            assert error['type'] == expected[index]['type']
            assert error['loc'] == expected[index]['loc']
