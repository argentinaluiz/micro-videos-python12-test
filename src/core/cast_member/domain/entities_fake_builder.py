# type: ignore
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, List, TypeVar
from faker import Faker
from .entities import CastMember, CastMemberId, CastMemberType

T = TypeVar('T')

PropOrFactory = T | Callable[['CastMemberFakerBuilder[Any]', int], T]


@dataclass(slots=True)
class CastMemberFakerBuilder(Generic[T]):
    count_objs: int = 1

    __cast_member_id: PropOrFactory[CastMemberId | None] = field(
        default=None, init=False
    )
    __name: PropOrFactory[str] = field(
        default=lambda self, index: Faker().name(), init=False
    )
    __type: PropOrFactory[CastMemberType] = field(
        default=lambda self, index: CastMember.DIRECTOR, init=False
    )
    __created_at: PropOrFactory[datetime] = field(
        default=None, init=False
    )

    @classmethod
    def a_director(cls) -> 'CastMemberFakerBuilder[CastMember]':
        return cls().with_type(CastMember.DIRECTOR)
    
    @classmethod
    def the_directors(cls, count: int) -> 'CastMemberFakerBuilder[List[CastMember]]':
        return cls(count).with_type(CastMember.DIRECTOR)
    
    @classmethod
    def an_actor(cls) -> 'CastMemberFakerBuilder[CastMember]':
        return cls().with_type(CastMember.ACTOR)
    
    @classmethod
    def the_actors(cls, count: int) -> 'CastMemberFakerBuilder[List[CastMember]]':
        return cls(count).with_type(CastMember.ACTOR)

    @classmethod
    def the_cast_members(cls, count: int) -> 'CastMemberFakerBuilder[List[CastMember]]':
        return cls(count)

    def with_cast_member_id(self, value: PropOrFactory[CastMemberId]):
        self.__cast_member_id = value
        return self

    def with_name(self, value: PropOrFactory[str]):
        self.__name = value
        return self

    def with_type(self, value: PropOrFactory[CastMemberType]):
        self.__type = value
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
        self.__type = value if value is not None else 'fake value'
        return self

    def build(self) -> T:
        cast_members = list(
            map(
                lambda index: CastMember(**{
                    **({
                        'cast_member_id': self.__call_factory(self.__cast_member_id, index),
                    } if self.__cast_member_id is not None else {}),
                    'name': self.__call_factory(self.__name, index),
                    'type': self.__call_factory(self.__type, index),
                    **({
                        'created_at': self.__call_factory(self.__created_at, index),
                    } if self.__created_at is not None else {}),
                }),
                list(range(self.count_objs))
            )
        )
        return cast_members if self.count_objs > 1 else cast_members[0]

    @property
    def cast_member_id(self) -> CastMemberId:
        value = self.__call_factory(self.__cast_member_id, 0)
        if value is None:
            raise ValueError(
                'Prop cast_member_id not have a factory, use "with methods"'
            )
        return value

    @property
    def name(self) -> str:
        return self.__call_factory(self.__name, 0)

    @property
    def type(self) -> CastMemberType:
        return self.__call_factory(self.__type, 0)

    @property
    def created_at(self) -> datetime:
        value = self.__call_factory(self.__created_at, 0)
        if value is None:
            raise ValueError(
                'Prop created_at not have a factory, use "with methods"'
            )
        return value

    def __call_factory(self, value: PropOrFactory[Any], index: int) -> Any:
        return value(self, index) if callable(value) else value
