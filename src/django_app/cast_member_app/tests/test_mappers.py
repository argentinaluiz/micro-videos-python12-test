import pytest
from django.utils import timezone
from core.cast_member.domain.entities import CastMember

from django_app.cast_member_app.models import CastMemberModel, CastMemberModelMapper

@pytest.mark.django_db
class TestCastMemberModelMapper:

    def test_to_entity(self):
        
        created_at = timezone.now()
        model = CastMemberModel(
            id='af46842e-027d-4c91-b259-3a3642144ba4',
            name='cast member test',
            type=CastMember.DIRECTOR,
            created_at=created_at
        )

        entity = CastMemberModelMapper.to_entity(model)
        assert entity.cast_member_id.id == 'af46842e-027d-4c91-b259-3a3642144ba4'
        assert entity.name == 'cast member test'
        assert entity.type == CastMember.DIRECTOR
        assert entity.created_at == created_at
        

    def test_to_model(self):
        entity = CastMember(
            name='cast member test',
            type=CastMember.DIRECTOR,
        )

        model = CastMemberModelMapper.to_model(entity)

        assert model.id == entity.cast_member_id.id
        assert model.name == 'cast member test'
        assert model.type == CastMember.DIRECTOR
        assert model.created_at == entity.created_at