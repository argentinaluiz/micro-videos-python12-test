from typing import Any, Dict, List
from urllib.parse import urlencode
from core.cast_member.application.use_cases import CastMemberOutput
from core.cast_member.domain.entities import CastMember, CastMemberId
from core.cast_member.domain.repositories import ICastMemberRepository
from core.shared.domain.exceptions import EntityValidationException, NotFoundException
from django_app.cast_member_app.api import CastMemberController
from .helpers import init_cast_member_controller_all_none
from django_app.cast_member_app.tests.fixtures import CreateCastMemberApiFixture, GetObjectCastMemberApiFixture, ListCastMembersApiFixture, UpdateCastMemberApiFixture
from django_app.shared_app.tests.helpers import make_request
from pydantic import ValidationError
import pytest
from django_app.ioc_app.containers import container


@pytest.mark.django_db
class TestCastMemberControllerPostMethodInt:

    controller: CastMemberController
    repo: ICastMemberRepository

    def setup_method(self):
        self.repo = container.cast_member.cast_member_repository_django_orm()
        self.controller = CastMemberController(**{
            **init_cast_member_controller_all_none(),  # type: ignore
            'create_use_case': container.cast_member.create_cast_member_use_case,
        })

    @pytest.mark.parametrize('request_body, exception', CreateCastMemberApiFixture.arrange_for_invalid_requests())
    def test_invalid_request(self, request_body: Dict[str, Any], exception: ValidationError):
        request = make_request(
            http_method='post', send_data=request_body)
        with pytest.raises(ValidationError) as assert_exception:
            self.controller.post(request)
        assert len(assert_exception.value.errors()) == len(exception.errors())
        # sourcery skip: no-loop-in-tests
        for assert_error, error in zip(assert_exception.value.errors(), exception.errors()):
            assert assert_error['type'] == error['type']
            assert assert_error['msg'] == error['msg']
            assert assert_error['loc'] == error['loc']

    @pytest.mark.parametrize('request_body, exception', CreateCastMemberApiFixture.arrange_for_entity_validation_error())
    def test_entity_validation_error(self, request_body: Dict[str, Any], exception: ValidationError):
        request = make_request(
            http_method='post', send_data=request_body)
        with pytest.raises(ValidationError) as assert_exception:
            self.controller.post(request)
        assert len(assert_exception.value.errors()) == len(exception.errors())
        # sourcery skip: no-loop-in-tests
        for assert_error, error in zip(assert_exception.value.errors(), exception.errors()):
            assert assert_error['type'] == error['type']
            assert assert_error['msg'] == error['msg']
            assert assert_error['loc'] == error['loc']

    @pytest.mark.parametrize('request_body, response_body', CreateCastMemberApiFixture.arrange_for_create())
    def test_post_method(self, request_body: Dict[str, Any], response_body: Dict[str, Any]):
        request = make_request(
            http_method='post', send_data=request_body)
        response = self.controller.post(request)
        response_data: Dict[str, Any] = response.data  # type: ignore
        assert response.status_code == 201
        assert 'data' in response_data
        assert CreateCastMemberApiFixture.keys_in_response() == list(
            response_data['data'].keys())

        data = response_data['data']
        cast_member_created = self.repo.find_by_id(CastMemberId(data['id']))
        assert cast_member_created is not None
        output = CastMemberOutput.from_entity(cast_member_created)
        serialized = CastMemberController.serialize(output)

        assert response.data == serialized  # type: ignore
        assert response.data == {  # type: ignore
            'data': {
                **response_body,
                'id': cast_member_created.cast_member_id.id,
                'created_at': serialized['data']['created_at']
            }
        }


@pytest.mark.django_db
class TestCastMemberControllerGetObjectMethodInt:

    controller: CastMemberController
    repo: ICastMemberRepository

    def setup_method(self):
        self.repo = container.cast_member.cast_member_repository_django_orm()
        self.controller = CastMemberController(**{
            **init_cast_member_controller_all_none(),  # type: ignore
            'get_use_case': container.cast_member.get_cast_member_use_case
        })

    def test_throw_exception_when_uuid_is_invalid(self):
        with pytest.raises(ValidationError) as assert_exception:
            self.controller.get_object('fake api')
        assert len(assert_exception.value.errors()) == 1
        assert assert_exception.value.errors()[0]['type'] == 'uuid_parsing'

    def test_throw_exception_when_cast_member_not_found(self):
        uuid_value = 'af46842e-027d-4c91-b259-3a3642144ba4'
        with pytest.raises(NotFoundException):
            self.controller.get_object(uuid_value)

    def test_get_object_method(self):
        cast_member = CastMember.fake().a_director().build()
        self.repo.insert(cast_member)

        response = self.controller.get_object(cast_member.cast_member_id.id)

        assert response.status_code == 200
        response_data: Dict[str, Any] = response.data  # type: ignore
        assert 'data' in response_data
        output = CastMemberOutput.from_entity(cast_member)
        serialized = CastMemberController.serialize(output)
        assert GetObjectCastMemberApiFixture.keys_in_cast_member_response() == list(
            response_data['data'].keys())
        assert response.data == serialized  # type: ignore

        assert response_data == {
            'data': {
                'id': cast_member.cast_member_id.id,
                'name': cast_member.name,
                'type': cast_member.type,
                'created_at': serialized['data']['created_at']
            }
        }


@pytest.mark.django_db
class TestCastMemberControllerGetMethodInt:

    controller: CastMemberController
    repo: ICastMemberRepository

    def setup_method(self):
        self.repo = container.cast_member.cast_member_repository_django_orm()
        self.controller = CastMemberController(**{
            **init_cast_member_controller_all_none(),  # type: ignore
            'list_use_case': container.cast_member.list_cast_members_use_case
        })

    @pytest.mark.parametrize(
        'request_query_params, expected_entities, expected_meta, entities',
        ListCastMembersApiFixture.arrange_incremented_with_created_at()
    )
    def test_execute_using_empty_search_params(self,
                                               request_query_params: Dict[str, Any],
                                               expected_entities: List[CastMember],
                                               expected_meta: Dict[str, Any],
                                               entities: List[CastMember]):
        self.repo.bulk_insert(entities)
        self.assert_response(request_query_params,
                             expected_entities, expected_meta)

    @pytest.mark.parametrize(
        'request_query_params, expected_entities, expected_meta, entities',
        ListCastMembersApiFixture.arrange_unsorted()
    )
    def test_execute_using_pagination_and_sort_and_filter(self,
                                                          request_query_params: Dict[str, Any],
                                                          expected_entities: List[CastMember],
                                                          expected_meta: Dict[str, Any],
                                                          entities: List[CastMember]):
        self.repo.bulk_insert(entities)
        self.assert_response(request_query_params,
                             expected_entities, expected_meta)

    def assert_response(self, send_data: Dict[str, Any], expected_entities: List[CastMember], expected_meta: Dict[str, Any]):
        request = make_request(
            http_method='get',
            url=f'/?{urlencode(send_data)}'
        )
        response = self.controller.get(request)

        assert response.status_code == 200
        print(expected_entities)
        assert response.data == {  # type: ignore
            'data': [self.serialize_cast_member(cast_member) for cast_member in expected_entities],
            'meta': expected_meta,
        }

    def serialize_cast_member(self, cast_member: CastMember):
        output = CastMemberOutput.from_entity(cast_member)
        return CastMemberController.serialize(output)['data']


@pytest.mark.django_db
class TestCastMemberControllerPatchMethodInt:

    controller: CastMemberController
    repo: ICastMemberRepository

    def setup_method(self):
        self.repo = container.cast_member.cast_member_repository_django_orm()
        self.controller = CastMemberController(**{
            **init_cast_member_controller_all_none(),  # type: ignore
            'update_use_case': container.cast_member.update_cast_member_use_case
        })

    @pytest.mark.parametrize('request_body, exception', UpdateCastMemberApiFixture.arrange_for_invalid_requests())
    def test_invalid_request(self, request_body: Dict[str, Any], exception: ValidationError):
        cast_member = CastMember.fake().a_director().build()
        self.repo.insert(cast_member)
        request = make_request(
            http_method='patch', send_data=request_body)
        with pytest.raises(ValidationError) as assert_exception:
            self.controller.patch(request, cast_member.cast_member_id.id)
        assert len(assert_exception.value.errors()) == len(exception.errors())
        # sourcery skip: no-loop-in-tests
        for assert_error, error in zip(assert_exception.value.errors(), exception.errors()):
            assert assert_error['type'] == error['type']
            assert assert_error['msg'] == error['msg']
            assert assert_error['loc'] == error['loc']

    @pytest.mark.parametrize('request_body, exception', UpdateCastMemberApiFixture.arrange_for_entity_validation_error())
    def test_entity_validation_error(self, request_body: Dict[str, Any], exception: EntityValidationException):
        cast_member = CastMember.fake().a_director().build()
        self.repo.insert(cast_member)
        request = make_request(
            http_method='patch', send_data=request_body)
        with pytest.raises(EntityValidationException) as assert_exception:
            self.controller.patch(request, cast_member.cast_member_id.id)
        assert assert_exception.value.errors == exception.errors

    def test_throw_exception_when_uuid_is_invalid(self):
        request = make_request(http_method='patch', send_data={})
        with pytest.raises(ValidationError) as assert_exception:
            self.controller.patch(request, 'fake api')
        assert assert_exception.value.errors()[0]['type'] == 'uuid_parsing'

    def test_throw_exception_when_cast_member_not_found(self):
        uuid_value = 'af46842e-027d-4c91-b259-3a3642144ba4'
        request = make_request(http_method='patch', send_data={'name': 'test'})
        with pytest.raises(NotFoundException):
            self.controller.patch(request, uuid_value)

    @pytest.mark.parametrize('request_body, response_body, entity', UpdateCastMemberApiFixture.arrange_for_update())
    def test_patch_method(self,
                        request_body: Dict[str, Any],
                        response_body: Dict[str, Any],
                        entity: CastMember):
        self.repo.insert(entity)
        request = make_request(
            http_method='put', send_data=request_body)
        response = self.controller.patch(request, entity.cast_member_id.id)

        response_data: Dict[str, Any] = response.data  # type: ignore
        assert response.status_code == 200
        assert 'data' in response_data
        assert CreateCastMemberApiFixture.keys_in_response() == list(
            response_data['data'].keys())

        data = response_data['data']
        cast_member_updated = self.repo.find_by_id(CastMemberId(data['id']))
        assert cast_member_updated is not None
        output = CastMemberOutput.from_entity(cast_member_updated)
        serialized = CastMemberController.serialize(output)

        assert response.data == serialized  # type: ignore
        assert response.data == {  # type: ignore
            'data': {
                'id': cast_member_updated.cast_member_id.id,
                'name': response_body.get('name', cast_member_updated.name),
                'type': response_body.get(
                    'type', cast_member_updated.type
                ),
                'created_at': serialized['data']['created_at'],
            }
        }


@pytest.mark.django_db
class TestCastMemberControllerDeleteMethodInt:

    controller: CastMemberController
    repo: ICastMemberRepository

    def setup_class(self):
        self.repo = container.cast_member.cast_member_repository_django_orm()
        self.controller = CastMemberController(**{
            **init_cast_member_controller_all_none(),  # type: ignore
            'delete_use_case': container.cast_member.delete_cast_member_use_case
        })

    def test_throw_exception_when_uuid_is_invalid(self):
        request = make_request(http_method='delete')
        with pytest.raises(ValidationError) as assert_exception:
            self.controller.delete(request, 'fake api')
        assert len(assert_exception.value.errors()) == 1
        assert assert_exception.value.errors()[0]['type'] == 'uuid_parsing'

    def test_throw_exception_when_cast_member_not_found(self):
        uuid_value = 'af46842e-027d-4c91-b259-3a3642144ba4'
        request = make_request(http_method='delete')
        with pytest.raises(NotFoundException):
            self.controller.delete(request, uuid_value)

    def test_delete_method(self):
        cast_member = CastMember.fake().a_director().build()
        self.repo.insert(cast_member)
        request = make_request(http_method='delete')
        response = self.controller.delete(request, cast_member.cast_member_id.id)

        assert response.status_code == 204
        assert self.repo.find_by_id(cast_member.cast_member_id) is None
