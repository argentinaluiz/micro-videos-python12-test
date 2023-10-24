from dataclasses import dataclass
from os import error
from typing import Any, Dict, List

class NotFoundException(Exception):

    def __init__(self, _id: Any | List[Any], entity_name: str):
        if isinstance(_id, list):
            _id = ', '.join(str(i) for i in _id)
        super().__init__(f'{entity_name} with id {_id} not found')


@dataclass(slots=True)
class EntityValidationException(Exception):

    errors: Dict[str, List[str] | str]
