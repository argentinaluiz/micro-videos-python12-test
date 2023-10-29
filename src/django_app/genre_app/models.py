from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Type
from core.category.domain.entities import CategoryId
from core.genre.domain.repositories import IGenreRepository
from core.genre.domain.entities import Genre, GenreId
from django.core.paginator import Paginator
from django.db import models
from core.shared.domain.exceptions import NotFoundException
from core.shared.domain.search_params import SortDirection

from django.db import connection
from django.db.models.expressions import RawSQL

from django_app.category_app.models import CategoryModel


class GenreModel(models.Model):

    id = models.UUIDField(primary_key=True, editable=True)
    name = models.CharField(max_length=255)
    categories = models.ManyToManyField(
        'category_app.CategoryModel', related_name='genres')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'genres'
        ordering = ['-created_at']


@dataclass
class GenreRelations:
    categories_ids: List[str]


class GenreModelMapper:

    @staticmethod
    def to_entity(model: GenreModel) -> Genre:
        print(model._prefetched_objects_cache)
        return Genre(
            genre_id=GenreId(model.id),
            name=model.name,
            categories_id={CategoryId(str(category.id))
                           for category in model._prefetched_objects_cache['categories']},
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: Genre) -> Tuple['GenreModel', GenreRelations]:
        return GenreModel(
            id=entity.genre_id.id,
            name=entity.name,
            created_at=entity.created_at,
        ), GenreRelations(
            categories_ids=[
                category_id.id for category_id in entity.categories_id]
        )


class GenreDjangoRepository(IGenreRepository):

    sortable_fields: List[str] = ['name', 'created_at']

    def insert(self, entity: Genre) -> None:
        model, relations = GenreModelMapper.to_model(entity)
        model.save()
        model.categories.set(relations.categories_ids)

    def bulk_insert(self, entities: List[Genre]) -> None:
        entities_and_relations = list(
            map(
                GenreModelMapper.to_model, entities
            )
        )
        models = GenreModel.objects.bulk_create(
            [entity for entity, _ in entities_and_relations]
        )
        for index, model in enumerate(models):
            model.categories.set(
                entities_and_relations[index][1].categories_ids
            )

    def find_by_id(self, entity_id: GenreId) -> Genre | None:
        model = self._get(entity_id)
        return GenreModelMapper.to_entity(model) if model else None

    def find_all(self) -> List[Genre]:
        return [
            GenreModelMapper.to_entity(model)
            for model in GenreModel.objects.prefetch_related(self._prefetch_categories()).all()
        ]

    def update(self, entity: Genre) -> None:
        count_updated = GenreModel.objects.filter(pk=entity.genre_id.id).update(
            name=entity.name,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )
        if not count_updated:
            raise NotFoundException(
                entity.genre_id.id, self.get_entity().__name__)

        categories_set = GenreModel.objects.get(
            pk=entity.genre_id.id).categories
        categories_set.clear()
        categories_set.add(
            *[category_id.id for category_id in entity.categories_id],
        )

    def delete(self, entity_id: GenreId) -> None:
        model = self._get(entity_id)
        if not model:
            raise NotFoundException(
                entity_id.id, self.get_entity().__name__)
        model.delete()

    def _get(self, entity_id: GenreId) -> GenreModel | None:
        return GenreModel.objects.filter(pk=entity_id.id)\
            .prefetch_related(self._prefetch_categories())\
            .first()

    def search(self, input_params: IGenreRepository.SearchParams) -> IGenreRepository.SearchResult:
        query = GenreModel.objects.all().distinct().prefetch_related(self._prefetch_categories())
        if input_params.filter:
            if input_params.filter.name:
                query = query.filter(name__icontains=input_params.filter.name)
            if input_params.filter.categories_id:
                query = query.filter(categories__id__in=[
                    category_id.id for category_id in input_params.filter.categories_id
                ])
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

        return IGenreRepository.SearchResult(
            items=[GenreModelMapper.to_entity(
                model) for model in page_obj.object_list],
            total=paginator.count,
            current_page=input_params.page,
            per_page=input_params.per_page,
        )

    def get_entity(self) -> Type[Genre]:
        return Genre

    def _prefetch_categories(self):
        return models.Prefetch(
            'categories',
            queryset=CategoryModel.objects.only('id'))
