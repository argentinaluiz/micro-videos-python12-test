# type: ignore
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, List, Set, TypeVar
from core.category.domain.entities import CategoryId
from faker import Faker
from .entities import Genre, GenreId

T = TypeVar('T')

PropOrFactory = T | Callable[['GenreFakerBuilder[Any]', int], T]


@dataclass(slots=True)
class GenreFakerBuilder(Generic[T]):
    count_objs: int = 1

    __genre_id: PropOrFactory[GenreId | None] = field(
        default=None, init=False
    )
    __name: PropOrFactory[str] = field(
        default=lambda self, index: Faker().name(), init=False
    )
    __categories_id: List[PropOrFactory[CategoryId]] = field(
        default_factory=list, init=False
    )
    __is_active: bool = field(default=lambda self, index: True, init=False)
    __created_at: PropOrFactory[datetime] = field(
        default=None, init=False
    )

    @classmethod
    def a_genre(cls) -> 'GenreFakerBuilder[Genre]':
        return cls()

    @classmethod
    def the_genres(cls, count: int) -> 'GenreFakerBuilder[List[Genre]]':
        return cls(count)

    def with_genre_id(self, value: PropOrFactory[GenreId]):
        self.__genre_id = value
        return self

    def with_name(self, value: PropOrFactory[str]):
        self.__name = value
        return self

    def add_category_id(self, value: PropOrFactory[CategoryId]):
        self.__categories_id.append(value)
        return self

    def activate(self):
        self.__is_active = True
        return self

    def deactivate(self):
        self.__is_active = False
        return self

    def with_created_at(self, value: PropOrFactory[datetime]):
        self.__created_at = value
        return self

    def with_invalid_name_too_long(self, value: str = None):
        self.__name = value if value is not None else ''.join(
            Faker().random_letters(length=256)
        )
        return self

    def with_invalid_type(self, value: Any = None):
        self.__categories_id = value if value is not None else 'fake value'
        return self

    def build(self) -> T:
        genre_ids = list(
            map(
                lambda index: Genre(**{
                    **({
                        'genre_id': self.__call_factory(self.__genre_id, index),
                    } if self.__genre_id is not None else {}),
                    'name': self.__call_factory(self.__name, index),
                    'categories_id': set(self.__call_factory(self.__categories_id, index))
                    if len(self.__categories_id)
                    else {CategoryId()},
                    **({
                        'created_at': self.__call_factory(self.__created_at, index),
                    } if self.__created_at is not None else {}),
                }),
                list(range(self.count_objs))
            )
        )
        return genre_ids if self.count_objs > 1 else genre_ids[0]

    @property
    def genre_id(self) -> GenreId:
        value = self.__call_factory(self.__genre_id, 0)
        if value is None:
            raise ValueError(
                'Prop genre_id not have a factory, use "with methods"'
            )
        return value

    @property
    def name(self) -> str:
        return self.__call_factory(self.__name, 0)

    @property
    def categories_id(self) -> List[CategoryId]:
        categories_id = self.__call_factory(self.__categories_id, 0)
        if not len(categories_id):
            categories_id = [CategoryId()]
        return categories_id

    @property
    def is_active(self) -> bool:
        return self.__call_factory(self.__is_active, 0)

    @property
    def created_at(self) -> datetime:
        value = self.__call_factory(self.__created_at, 0)
        if value is None:
            raise ValueError(
                'Prop created_at not have a factory, use "with methods"'
            )
        return value

    def __call_factory(self, value: PropOrFactory[Any] | List[PropOrFactory[Any]], index: int) -> Any:
        if isinstance(value, Callable):
            return value(self, index)

        if isinstance(value, list):
            map_func = lambda item: self.__call_factory(item[1], item[0])
            return list(map(map_func, enumerate(value)))

        return value
