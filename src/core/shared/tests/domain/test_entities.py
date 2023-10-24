

from abc import ABC
from pydantic import ValidationError
from pydantic.dataclasses import dataclass
from core.shared.domain.entities import Entity
from core.shared.domain.notification import Notification
from core.shared.domain.value_objects import Uuid


class TestEntity:

    @dataclass(slots=True, kw_only=True)
    class StubEntity(Entity):
        _entity_id: Uuid
        name: str

        @property
        def entity_id(self) -> Uuid:
            return self._entity_id

        def validate(self):
            self._validate({
                '_entity_id': self.entity_id,
                'name': self.name
            })

    def test_should_create_a_notification(self):
        entity = TestEntity.StubEntity(_entity_id=Uuid(), name='stub')
        assert entity.notification is not None
        assert isinstance(entity.notification, Notification)

    def test__validate(self):
        entity = TestEntity.StubEntity(_entity_id=Uuid(), name='stub')
        entity.name = 1  # type: ignore
        entity.validate()
        assert entity.notification.has_errors() is True
        assert len(entity.notification.errors) == 1
        assert entity.notification.errors == {
            'name': ['Input should be a valid string']
        }

    def test_should_be_a_abc_subclass(self):
        assert issubclass(Entity, ABC)

    def test_should_be_equal_to_another_entity_with_the_same_id(self):

        entity_id = Uuid()
        entity1 = TestEntity.StubEntity(_entity_id=entity_id, name='stub1')
        entity2 = TestEntity.StubEntity(_entity_id=entity_id, name='stub2')
        assert entity1.equals(entity2)

    def test_should_not_be_equal_to_another_entity_with_a_different_id(self):

        entity1 = TestEntity.StubEntity(_entity_id=Uuid(), name='stub1')
        entity2 = TestEntity.StubEntity(_entity_id=Uuid(), name='stub1')
        assert entity1 != entity2
