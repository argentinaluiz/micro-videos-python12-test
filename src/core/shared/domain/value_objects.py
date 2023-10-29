import abc
from abc import ABC
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4, UUID as PythonUUID


class ValueObject(ABC):

    @abc.abstractmethod
    def equals(self, other: Any) -> bool:
        raise NotImplementedError


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
        except AttributeError as ex:
            raise InvalidUuidException(self.id) from ex

    def __str__(self):
        return self.id
    
    def __eq__(self, __value: object) -> bool:
        return self.equals(__value)

    def equals(self, other: Any) -> bool:
        return self.id == other.id if isinstance(other, self.__class__) else False


class InvalidUuidException(Exception):
    def __init__(self, _id: str):
        super().__init__(f'ID {_id} must be a valid UUID')
