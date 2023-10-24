from typing import List, Type
from core.category.domain.repositories import ICategoryRepository
from core.category.domain.entities import Category
from django.core.paginator import Paginator
from django.db import models
from core.shared.domain.exceptions import NotFoundException
from core.shared.domain.search_params import SortDirection

from core.shared.domain.value_objects import Uuid
from django.db import connection
from django.db.models.expressions import RawSQL


class CategoryModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:  # type: ignore
        db_table = 'categories'
        ordering = ['-created_at']


class CategoryModelMapper:

    @staticmethod
    def to_entity(model: 'CategoryModel') -> Category:
        return Category(
            category_id=Uuid(str(model.id)),
            name=model.name,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: Category) -> 'CategoryModel':
        return CategoryModel(
            id=entity.category_id.id,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )


class CategoryDjangoRepository(ICategoryRepository):

    sortable_fields: List[str] = ['name', 'created_at']

    def insert(self, entity: Category) -> None:
        model = CategoryModelMapper.to_model(entity)
        model.save()

    def bulk_insert(self, entities: List[Category]) -> None:
        CategoryModel.objects.bulk_create(
            list(
                map(
                    CategoryModelMapper.to_model, entities
                )
            )
        )

    def find_by_id(self, entity_id: Uuid) -> Category | None:
        model = self._get(entity_id)
        return CategoryModelMapper.to_entity(model) if model else None

    def find_all(self) -> List[Category]:
        return [CategoryModelMapper.to_entity(model) for model in CategoryModel.objects.all()]

    def update(self, entity: Category) -> None:
        count_updated = CategoryModel.objects.filter(pk=entity.category_id.id).update(
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )
        if not count_updated:
            raise NotFoundException(
                entity.category_id.id, self.get_entity().__name__)

    def delete(self, entity_id: Uuid) -> None:
        model = self._get(entity_id)
        if not model:
            raise NotFoundException(
                entity_id.id, self.get_entity().__name__)
        model.delete()

    def _get(self, entity_id: Uuid) -> CategoryModel | None:
        return CategoryModel.objects.filter(pk=entity_id.id).first()

    def search(self, input_params: ICategoryRepository.SearchParams) -> ICategoryRepository.SearchResult:
        query = CategoryModel.objects.all()

        if input_params.filter:
            query = query.filter(name__icontains=input_params.filter)
        if input_params.sort and input_params.sort in self.sortable_fields:
            if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
                raw_order = RawSQL(f'binary {input_params.sort}',[])
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

        return ICategoryRepository.SearchResult(
            items=[CategoryModelMapper.to_entity(
                model) for model in page_obj.object_list],
            total=paginator.count,
            current_page=input_params.page,
            per_page=input_params.per_page,
        )

    def get_entity(self) -> Type[Category]:
        return Category
