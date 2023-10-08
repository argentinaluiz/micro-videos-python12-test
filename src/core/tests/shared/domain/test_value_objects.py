

from abc import ABC
from uuid import UUID as PythonUUID
import pytest
from core.shared.domain.value_objects import InvalidUuidException, Uuid, ValueObject


class TestValueObject:

    def test_should_be_a_abc_subclass(self):
        assert issubclass(ValueObject, ABC)


class TestUuid:

    def test_should_be_a_value_object_subclass(self):
        assert issubclass(ValueObject, ABC)

    def test_should_be_freeze(self):
        assert Uuid.__dataclass_params__.frozen is True  # pylint: disable=no-member # type: ignore

    def test_should_be_slots(self):
        assert Uuid.__dataclass_params__.slots is True  # pylint: disable=no-member # type: ignore

    def test_should_throw_an_exception_when_invalid_uuid(self):
        with pytest.raises(InvalidUuidException) as assert_exception:
            Uuid('not-a-uuid')
        assert str(assert_exception.value) == 'ID not-a-uuid must be a valid UUID'

    def test_should_return_a_valid_uuid(self):
        vo = Uuid()
        assert vo.id is not None
        assert isinstance(vo.id, str)
        try:
            PythonUUID(vo.id)
        except ValueError:
            pytest.fail('Invalid UUID')
