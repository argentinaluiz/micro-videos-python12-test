from abc import ABC
from dataclasses import dataclass, field
from typing import Any, List

from core.shared.application.use_cases import PaginationOutput
from pydantic import TypeAdapter


class ResourcePresenter(ABC):

    def serialize(self):
        data = TypeAdapter(self.__class__).dump_python(self)
        return {'data': data}


@dataclass(slots=True)
class CollectionPresenter(ABC):
    data: List[Any] = field(init=False)
    pagination: PaginationOutput[Any] | None = field(init=False, default=None)

    def serialize(self):
        data = [TypeAdapter(item.__class__).dump_python(item)
                for item in self.data]
        meta = {
            'total': self.pagination.total,
            'current_page': self.pagination.current_page,
            'per_page': self.pagination.per_page,
            'last_page': self.pagination.last_page
        } if self.pagination is not None else None
        return {
            'data': data,
            'meta': meta
        }
