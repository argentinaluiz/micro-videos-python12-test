
from datetime import datetime
from core.cast_member.domain.entities import CastMember, CastMemberId, CastMemberType

from core.cast_member.domain.entities_fake_builder import CastMemberFakerBuilder
import pytest


class TestCastMemberFakeBuilder:

    def test_cast_member_id_prop_throw_exception_when_is_none(self):
        with pytest.raises(ValueError) as assert_exception:
            faker = CastMemberFakerBuilder.a_director()
            faker.cast_member_id  # pylint: disable=pointless-statement
        assert str(
            assert_exception.value) == 'Prop cast_member_id not have a factory, use "with methods"'

    def test_cast_member_id_prop(self):
        faker = CastMemberFakerBuilder.a_director()
        cast_member_id = CastMemberId()
        this = faker.with_cast_member_id(cast_member_id)

        assert isinstance(this, CastMemberFakerBuilder)
        assert faker.cast_member_id == cast_member_id

    def test_invalid_cases_for_name_prop(self):
        faker = CastMemberFakerBuilder.a_director()

        name_value = faker.with_invalid_name_too_long().name
        assert len(name_value) == 256

    def test_name_prop(self):
        faker = CastMemberFakerBuilder.a_director()
        assert isinstance(faker.name, str)

        this = faker.with_name('name test')
        assert isinstance(this, CastMemberFakerBuilder)
        assert faker.name == 'name test'

    def test_type_prop(self):
        faker = CastMemberFakerBuilder.a_director()
        assert faker.type == CastMember.DIRECTOR

        this = faker.with_type(CastMember.ACTOR)
        assert isinstance(this, CastMemberFakerBuilder)
        assert faker.type == CastMember.ACTOR

    def test_created_at_prop_throw_exception_when_is_none(self):
        with pytest.raises(Exception) as assert_exception:
            faker = CastMemberFakerBuilder.a_director()
            faker.created_at  # pylint: disable=pointless-statement
        assert str(
            assert_exception.value) == 'Prop created_at not have a factory, use "with methods"'

    def test_created_at_prop(self):
        faker = CastMemberFakerBuilder.a_director()
        date = datetime.now()
        this = faker.with_created_at(date)

        assert isinstance(this, CastMemberFakerBuilder)
        assert faker.created_at == date

    def test_build_a_cast_member(self):
        faker = CastMemberFakerBuilder.a_director()
        cast_member = faker.build()

        self.assert_props_types(cast_member)

        cast_member_id = CastMemberId()
        date = datetime.now()
        builder = faker.with_cast_member_id(cast_member_id)\
            .with_name('name test')\
            .with_type(CastMember.ACTOR)\
            .with_created_at(date)

        cast_member = builder.build()
        assert cast_member is not None
        self.assert_cast_member(
            cast_member, cast_member_id, date, CastMember.ACTOR)

    def test_build_the_cast_members(self):
        faker = CastMemberFakerBuilder.the_cast_members(2)
        cast_members = faker.build()

        assert cast_members is not None
        assert isinstance(cast_members, list)
        assert len(cast_members) == 2

        for cast_member in cast_members:  # sourcery skip: no-loop-in-tests
            self.assert_props_types(cast_member)

        cast_member_id = CastMemberId()
        date = datetime.now()
        builder = faker.with_cast_member_id(cast_member_id)\
            .with_name('name test')\
            .with_type(CastMember.ACTOR)\
            .with_created_at(date)

        cast_members = builder.build()

        for cast_member in cast_members:
            self.assert_cast_member(
                cast_member, cast_member_id, date, CastMember.ACTOR)

    def test_build_the_directors(self):
        faker = CastMemberFakerBuilder.the_directors(2)
        cast_members = faker.build()

        assert cast_members is not None
        assert isinstance(cast_members, list)
        assert len(cast_members) == 2

        for cast_member in cast_members:
            self.assert_props_types(cast_member)
            assert cast_member.type == CastMember.DIRECTOR

    def test_build_the_actors(self):
        faker = CastMemberFakerBuilder.the_actors(2)
        cast_members = faker.build()

        assert cast_members is not None
        assert isinstance(cast_members, list)
        assert len(cast_members) == 2

        for cast_member in cast_members:
            self.assert_props_types(cast_member)
            assert cast_member.type == CastMember.ACTOR

    def assert_props_types(self, cast_member: CastMember):
        assert cast_member is not None
        assert isinstance(cast_member.cast_member_id, CastMemberId)
        assert isinstance(cast_member.name, str)
        assert isinstance(cast_member.type, int)
        assert isinstance(cast_member.created_at, datetime)

    def assert_cast_member(self, cast_member: CastMember, cast_member_id: CastMemberId, created_at: datetime, type: CastMemberType):
        assert cast_member.cast_member_id == cast_member_id
        assert cast_member.name == 'name test'
        assert cast_member.type == type
        assert cast_member.created_at == created_at
