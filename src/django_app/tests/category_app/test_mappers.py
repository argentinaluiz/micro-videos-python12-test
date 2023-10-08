import pytest
from django.utils import timezone
from core.category.domain.entities import Category

from django_app.category_app.models import CategoryModel, CategoryModelMapper

@pytest.mark.django_db
class TestCategoryModelMapper:

    def test_to_entity(self):
        
        created_at = timezone.now()
        model = CategoryModel(
            id='af46842e-027d-4c91-b259-3a3642144ba4',
            name='Movie',
            description='Movie description',
            is_active=True,
            created_at=created_at
        )

        entity = CategoryModelMapper.to_entity(model)
        assert entity.category_id.id == 'af46842e-027d-4c91-b259-3a3642144ba4'
        assert entity.name == 'Movie'
        assert entity.description == 'Movie description'
        assert entity.is_active
        assert entity.created_at == created_at
        

    def test_to_model(self):
        entity = Category(
            name='Movie',
            description='Movie description',
            is_active=True,
        )

        model = CategoryModelMapper.to_model(entity)

        assert model.id == entity.category_id.id
        assert model.name == 'Movie'
        assert model.description == 'Movie description'
        assert model.is_active
        assert model.created_at == entity.created_at