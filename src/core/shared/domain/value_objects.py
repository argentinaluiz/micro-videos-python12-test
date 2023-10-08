from abc import ABC
from dataclasses import dataclass, field
from uuid import uuid4, UUID as PythonUUID


class ValueObject(ABC):
    pass


@dataclass(frozen=True, slots=True)
class Uuid(ValueObject):
    id: str = field(
        default_factory=lambda: str(uuid4()),
    )

    def __post_init__(self):
        id_value = str(self.id) if isinstance(self.id, PythonUUID) else self.id
        object.__setattr__(self, 'id', id_value)
        self.__validate()

    def __validate(self):
        try:
            PythonUUID(self.id)
        except ValueError as ex:
            raise InvalidUuidException(self.id) from ex


class InvalidUuidException(Exception):
    def __init__(self, id: str):
        super().__init__(f'ID {id} must be a valid UUID')
