# pylint: disable=protected-access,no-member # type: ignore
import unittest
from core.category.domain.entities import Category
from django_app.ioc_app.containers import container
import pytest
from django.db import models
from django.utils import timezone

from django_app.genre_app.models import GenreModel

@pytest.mark.django_db()
class TestGenreModel(unittest.TestCase):

    def test_mapping(self):
        table_name = GenreModel._meta.db_table
        self.assertEqual(table_name, 'genres')

        fields_name = tuple(field.name for field in GenreModel._meta.fields)
        self.assertEqual(fields_name, ('id', 'name', 'is_active', 'created_at'))

        id_field: models.UUIDField = GenreModel.id.field
        self.assertIsInstance(id_field, models.UUIDField)
        self.assertTrue(id_field.primary_key)
        self.assertIsNone(id_field.db_column)
        self.assertTrue(id_field.editable)

        name_field: models.CharField = GenreModel.name.field
        self.assertIsInstance(name_field, models.CharField)
        self.assertIsNone(name_field.db_column)
        self.assertFalse(name_field.null)
        self.assertFalse(name_field.blank)
        self.assertEqual(name_field.max_length, 255)

        categories_field = GenreModel.categories.field
        self.assertIsInstance(categories_field, models.ManyToManyField)

        is_active_field: models.BooleanField = GenreModel.is_active.field
        self.assertIsInstance(is_active_field, models.BooleanField)
        self.assertIsNone(is_active_field.db_column)
        self.assertFalse(is_active_field.null)
        self.assertFalse(is_active_field.blank)
        self.assertTrue(is_active_field.default)


        created_at_field: models.DateTimeField = GenreModel.created_at.field
        self.assertIsInstance(created_at_field, models.DateTimeField)
        self.assertIsNone(created_at_field.db_column)
        self.assertFalse(created_at_field.null)


    def test_create(self):
        category_repo = container.category.category_repository_django_orm()
        category = Category.fake().a_category().build()
        category_repo.insert(category)
        arrange = {
            'id': 'af46842e-027d-4c91-b259-3a3642144ba4',
            'name': 'genre test',
            'is_active': True,
            'created_at': timezone.now()
        }
        genre = GenreModel.objects.create(**arrange)
        genre.categories.add(category.category_id.id)

        self.assertEqual(genre.id, arrange['id'])
        self.assertEqual(genre.name, arrange['name'])
        self.assertEqual(genre.is_active, arrange['is_active'])
        self.assertEqual(genre.created_at, arrange['created_at'])
        self.assertEqual(str(genre.categories.first().id), category.category_id.id)
