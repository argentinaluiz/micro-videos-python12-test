# pylint: disable=protected-access,no-member # type: ignore
import unittest
from core.cast_member.domain.entities import CastMember
import pytest
from django.db import models
from django.utils import timezone

from django_app.cast_member_app.models import CastMemberModel

@pytest.mark.django_db()
class TestCastMemberModel(unittest.TestCase):


    def test_mapping(self):
        table_name = CastMemberModel._meta.db_table
        self.assertEqual(table_name, 'cast_members')

        fields_name = tuple(field.name for field in CastMemberModel._meta.fields)
        self.assertEqual(fields_name, ('id', 'name', 'type', 'created_at'))

        id_field: models.UUIDField = CastMemberModel.id.field
        self.assertIsInstance(id_field, models.UUIDField)
        self.assertTrue(id_field.primary_key)
        self.assertIsNone(id_field.db_column)
        self.assertTrue(id_field.editable)

        name_field: models.CharField = CastMemberModel.name.field
        self.assertIsInstance(name_field, models.CharField)
        self.assertIsNone(name_field.db_column)
        self.assertFalse(name_field.null)
        self.assertFalse(name_field.blank)
        self.assertEqual(name_field.max_length, 255)

        type_field: models.PositiveSmallIntegerField = CastMemberModel.type.field
        self.assertIsInstance(type_field, models.PositiveSmallIntegerField)
        self.assertIsNone(type_field.db_column)
        self.assertFalse(type_field.null)
        self.assertFalse(type_field.blank)
        self.assertEqual(type_field.choices, CastMemberModel.TYPES_CHOICES)


        created_at_field: models.DateTimeField = CastMemberModel.created_at.field
        self.assertIsInstance(created_at_field, models.DateTimeField)
        self.assertIsNone(created_at_field.db_column)
        self.assertFalse(created_at_field.null)

    def test_create(self):
        arrange = {
            'id': 'af46842e-027d-4c91-b259-3a3642144ba4',
            'name': 'Movie',
            'type': CastMember.DIRECTOR,
            'created_at': timezone.now()
        }
        category = CastMemberModel.objects.create(**arrange)
        self.assertEqual(category.id, arrange['id'])
        self.assertEqual(category.name, arrange['name'])
        self.assertEqual(category.type, arrange['type'])
        self.assertEqual(category.created_at, arrange['created_at'])
