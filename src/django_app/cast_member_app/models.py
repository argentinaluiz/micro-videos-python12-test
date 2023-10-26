from typing import List, Type
from core.cast_member.domain.repositories import ICastMemberRepository
from core.cast_member.domain.entities import CastMember, CastMemberId
from django.core.paginator import Paginator
from django.db import models
from core.shared.domain.exceptions import NotFoundException
from core.shared.domain.search_params import SortDirection

from django.db import connection
from django.db.models.expressions import RawSQL


class CastMemberModel(models.Model):

    TYPES_CHOICES = [
        (CastMember.DIRECTOR, 'Diretor'),
        (CastMember.ACTOR, 'Ator'),
    ]

    id = models.UUIDField(primary_key=True, editable=True)
    name = models.CharField(max_length=255)
    type = models.PositiveSmallIntegerField(
        choices=TYPES_CHOICES,
    )
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'cast_members'
        ordering = ['-created_at']


class CastMemberModelMapper:

    @staticmethod
    def to_entity(model: 'CastMemberModel') -> CastMember:
        return CastMember(
            cast_member_id=CastMemberId(str(model.id)),
            name=model.name,
            type=model.type,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: CastMember) -> 'CastMemberModel':
        return CastMemberModel(
            id=entity.cast_member_id.id,
            name=entity.name,
            type=entity.type,
            created_at=entity.created_at,
        )


class CastMemberDjangoRepository(ICastMemberRepository):

    sortable_fields: List[str] = ['name', 'created_at']

    def insert(self, entity: CastMember) -> None:
        model = CastMemberModelMapper.to_model(entity)
        model.save()

    def bulk_insert(self, entities: List[CastMember]) -> None:
        CastMemberModel.objects.bulk_create(
            list(
                map(
                    CastMemberModelMapper.to_model, entities
                )
            )
        )

    def find_by_id(self, entity_id: CastMemberId) -> CastMember | None:
        model = self._get(entity_id)
        return CastMemberModelMapper.to_entity(model) if model else None

    def find_all(self) -> List[CastMember]:
        return [CastMemberModelMapper.to_entity(model) for model in CastMemberModel.objects.all()]

    def update(self, entity: CastMember) -> None:
        count_updated = CastMemberModel.objects.filter(pk=entity.cast_member_id.id).update(
            name=entity.name,
            type=entity.type,
            created_at=entity.created_at,
        )
        if not count_updated:
            raise NotFoundException(
                entity.cast_member_id.id, self.get_entity().__name__)

    def delete(self, entity_id: CastMemberId) -> None:
        model = self._get(entity_id)
        if not model:
            raise NotFoundException(
                entity_id.id, self.get_entity().__name__)
        model.delete()

    def _get(self, entity_id: CastMemberId) -> CastMemberModel | None:
        return CastMemberModel.objects.filter(pk=entity_id.id).first()

    def search(self, input_params: ICastMemberRepository.SearchParams) -> ICastMemberRepository.SearchResult:
        query = CastMemberModel.objects.all()
        print(input_params.filter)
        if input_params.filter:
            if input_params.filter.name:
                query = query.filter(name__icontains=input_params.filter.name)
            if input_params.filter.type:
                query = query.filter(type=input_params.filter.type)
        if input_params.sort and input_params.sort in self.sortable_fields:
            if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
                raw_order = RawSQL(f'binary {input_params.sort}', [])
                query = query.order_by(
                    raw_order.asc() if input_params.sort_dir == SortDirection.ASC else raw_order.desc()
                )
            else:
                query = query.order_by(
                    input_params.sort if input_params.sort_dir == SortDirection.ASC else f'-{input_params.sort}'
                )

        else:
            query = query.order_by('-created_at')
        paginator = Paginator(query, input_params.per_page)
        page_obj = paginator.page(input_params.page)

        return ICastMemberRepository.SearchResult(
            items=[CastMemberModelMapper.to_entity(
                model) for model in page_obj.object_list],
            total=paginator.count,
            current_page=input_params.page,
            per_page=input_params.per_page,
        )

    def get_entity(self) -> Type[CastMember]:
        return CastMember
