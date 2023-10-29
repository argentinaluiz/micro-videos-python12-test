from uuid import UUID
from core.category.domain.entities import CategoryId
from django_app.category_app.models import CategoryModel
import pytest
from django.utils import timezone
from core.genre.domain.entities import Genre

from django_app.genre_app.models import GenreModel, GenreModelMapper

@pytest.mark.django_db
class TestGenreModelMapper:

    def test_to_entity(self):
        
        created_at = timezone.now()
        genre = GenreModel(
            id=UUID('af46842e-027d-4c91-b259-3a3642144ba4'),
            name='genre test',
            is_active=True,
            created_at=created_at
        )
        genre._prefetched_objects_cache = {
            'categories': [CategoryModel(
                id=UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
            )]
        }
        entity = GenreModelMapper.to_entity(genre)
        assert entity.genre_id.id == 'af46842e-027d-4c91-b259-3a3642144ba4'
        assert entity.name == 'genre test'
        assert entity.categories_id == {CategoryId('6ba7b810-9dad-11d1-80b4-00c04fd430c8')}
        assert entity.is_active == True
        assert entity.created_at == created_at
        

    def test_to_model(self):
        entity = Genre(
            name='genre test',
            categories_id={CategoryId('6ba7b810-9dad-11d1-80b4-00c04fd430c8')},
            is_active=True
        )

        model, relations = GenreModelMapper.to_model(entity)

        assert model.id == entity.genre_id.id
        assert model.name == 'genre test'
        assert model.is_active is True
        assert model.created_at == entity.created_at
        assert relations.categories_ids == ['6ba7b810-9dad-11d1-80b4-00c04fd430c8']
