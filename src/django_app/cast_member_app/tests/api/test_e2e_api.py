from urllib.parse import urlencode
from core.cast_member.application.use_cases import CastMemberOutput
from core.cast_member.domain.entities import CastMember, CastMemberId
from core.cast_member.domain.repositories import ICastMemberRepository
from core.shared.domain.exceptions import EntityValidationException
from django_app.cast_member_app.api import CastMemberController
from django_app.cast_member_app.tests.fixtures import CreateCastMemberApiFixture, ListCastMembersApiFixture, UpdateCastMemberApiFixture
import pytest
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIClient
from django_app.ioc_app.containers import container
from typing import Any, Dict, List
from pydantic import ValidationError


@pytest.mark.django_db
@pytest.mark.group('e2e')
class TestCastMembersPostE2E:

    client_http: APIClient
    cast_member_repository: ICastMemberRepository
    cast_member_controller: CastMemberController

    def setup_method(self):
        self.client_http = APIClient()
        self.cast_member_repository = container.cast_member.cast_member_repository_django_orm()

    @pytest.mark.parametrize('request_body, exception', CreateCastMemberApiFixture.arrange_for_invalid_requests())
    def test_invalid_request(self, request_body: Dict[str, Any], exception: ValidationError):
        response = self.client_http.post(
            '/cast-members/', data=request_body, format='json')
        assert response.status_code == 422  # type: ignore
        errors = [{error['loc'][-1]: [error['msg']]}
                  for error in exception.errors()]
        assert response.content == JSONRenderer().render(errors)  # type: ignore

    @pytest.mark.parametrize('request_body, exception', CreateCastMemberApiFixture.arrange_for_entity_validation_error())
    def test_entity_validation_error(self, request_body: Dict[str, Any], exception: ValidationError):
        response = self.client_http.post(
            '/cast-members/', data=request_body, format='json')
        assert response.status_code == 422  # type: ignore
        errors = [{error['loc'][-1]: [error['msg']]}
                  for error in exception.errors()]
        assert response.content == JSONRenderer().render(errors)  # type: ignore

    @pytest.mark.parametrize('request_body, expected_response_body', CreateCastMemberApiFixture.arrange_for_create())
    def test_post_method(self, request_body: Dict[str, Any], expected_response_body: Dict[str, Any]):
        response = self.client_http.post(
            '/cast-members/', data=request_body, format='json')
        assert response.status_code == 201  # type: ignore
        data = response.data['data']  # type: ignore
        assert CreateCastMemberApiFixture.keys_in_response() == list(data.keys())
        cast_member_created = self.cast_member_repository.find_by_id(
            CastMemberId(data['id']))
        output = CastMemberOutput.from_entity(cast_member_created)  # type: ignore
        serialized = CastMemberController.serialize(output)
        assert response.content == JSONRenderer().render(serialized)  # type: ignore
        assert response.data == {  # type: ignore
            'data': {
                **expected_response_body,
                'id': cast_member_created.cast_member_id.id,  # type: ignore
                'created_at': serialized['data']['created_at'],
            }
        }


@pytest.mark.django_db
@pytest.mark.group('e2e')
class TestCastMembersGetObjectE2E:

    client_http: APIClient
    cast_member_repository: ICastMemberRepository
    cast_member_controller: CastMemberController

    def setup_method(self):
        self.client_http = APIClient()
        self.cast_member_repository = container.cast_member.cast_member_repository_django_orm()

    def test_invalid_request(self):
        arrange = [
            {
                'id': 'e526ad81-a291-485b-808b-91d67716db3f',
                'expected': {
                    'status_code': 404,
                    'content': {'message': "CastMember with id e526ad81-a291-485b-808b-91d67716db3f not found"}
                }
            },
            {
                'id': 'fake id',
                'expected': {
                    'status_code': 422,
                    'content': [
                        {"id": [
                            "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `k` at 3"
                        ]}]
                }
            }
        ]

        for item in arrange:
            response = self.client_http.get(
                f'/cast-members/{item["id"]}/', format='json')
            assert response.status_code == item['expected']['status_code'] # type: ignore
            assert response.content == JSONRenderer().render(  # type: ignore
                item['expected']['content'])

    def test_get_object_method(self):
        cast_member_created = CastMember.fake().a_director().build()
        self.cast_member_repository.insert(cast_member_created)
        response = self.client_http.get(
            f'/cast-members/{cast_member_created.cast_member_id.id}/', format='json')
        assert response.status_code == 200  # type: ignore
        output = CastMemberOutput.from_entity(cast_member_created)
        serialized = CastMemberController.serialize(output)
        assert response.content == JSONRenderer().render(serialized)  # type: ignore


@pytest.mark.django_db
@pytest.mark.group('e2e')
class TestCastMembersGetE2E:

    client_http: APIClient
    cast_member_repository: ICastMemberRepository
    cast_member_controller: CastMemberController

    def setup_method(self):
        self.client_http = APIClient()
        self.cast_member_repository = container.cast_member.cast_member_repository_django_orm()

    @pytest.mark.parametrize(
        'request_query_params, expected_entities, expected_meta, entities',
        ListCastMembersApiFixture.arrange_incremented_with_created_at()
    )
    def test_execute_using_empty_search_params(self,
                                               request_query_params: Dict[str, Any],
                                               expected_entities: List[CastMember],
                                               expected_meta: Dict[str, Any],
                                               entities: List[CastMember]):
        self.cast_member_repository.bulk_insert(entities)
        self.assert_response(request_query_params,
                             expected_entities, expected_meta)

    @pytest.mark.parametrize(
        'request_query_params, expected_entities, expected_meta, entities',
        ListCastMembersApiFixture.arrange_unsorted())
    def test_execute_using_pagination_and_sort_and_filter(self, request_query_params: Dict[str, Any],
                                                          expected_entities: List[CastMember],
                                                          expected_meta: Dict[str, Any],
                                                          entities: List[CastMember]):
        self.cast_member_repository.bulk_insert(entities)
        self.assert_response(request_query_params,
                             expected_entities, expected_meta)

    def assert_response(self, send_data: dict, entities: List[CastMember], expected_meta: Dict[str, Any]):
        response = self.client_http.get(
            f'/cast-members/?{urlencode(send_data)}', format='json')

        assert response.status_code == 200  # type: ignore
        assert response.data == {  # type: ignore
            'data': [self.serialize_cast_member(cast_member) for cast_member in entities],
            'meta': expected_meta,
        }

    def serialize_cast_member(self, cast_member: CastMember):
        output = CastMemberOutput.from_entity(cast_member)
        return CastMemberController.serialize(output)['data']


@pytest.mark.django_db
@pytest.mark.group('e2e')
class TestCastMembersPatchE2E:

    client_http: APIClient
    cast_member_repository: ICastMemberRepository
    cast_member_controller: CastMemberController

    def setup_method(self):
        self.client_http = APIClient()
        self.cast_member_repository = container.cast_member.cast_member_repository_django_orm()

    @pytest.mark.parametrize('request_body, exception', UpdateCastMemberApiFixture.arrange_for_invalid_requests())
    def test_invalid_request(self, request_body: Dict[str, Any], exception: ValidationError):
        response = self.client_http.patch(
            '/cast-members/e526ad81-a291-485b-808b-91d67716db3f/', data=request_body, format='json')
        assert response.status_code == 422  # type: ignore
        errors = [{error['loc'][-1]: [error['msg']]}
                  for error in exception.errors()]
        assert response.content == JSONRenderer().render(errors)  # type: ignore

    @pytest.mark.parametrize('request_body, exception', UpdateCastMemberApiFixture.arrange_for_entity_validation_error())
    def test_entity_validation_error(self, request_body: Dict[str, Any], exception: EntityValidationException):
        cast_member = CastMember.fake().a_director().build()
        self.cast_member_repository.insert(cast_member)
        response = self.client_http.patch(
            f'/cast-members/{cast_member.cast_member_id.id}/', data=request_body, format='json')
        assert response.status_code == 422  # type: ignore
        errors = [{key: error} for key, error in exception.errors.items()]
        assert response.content == JSONRenderer().render(errors)  # type: ignore

    @pytest.mark.parametrize('request_body, response_body, entity', UpdateCastMemberApiFixture.arrange_for_update())
    def test_patch_method(self,
                          request_body: Dict[str, Any],
                          response_body: Dict[str, Any],
                          entity: CastMember):
        self.cast_member_repository.insert(entity)
        response = self.client_http.patch(
            f'/cast-members/{entity.cast_member_id.id}/', data=request_body, format='json')
        assert response.status_code == 200 # type: ignore
        assert 'data' in response.data # type: ignore
        data = response.data['data'] # type: ignore
        assert UpdateCastMemberApiFixture.keys_in_response() == list(data.keys())
        cast_member_updated = self.cast_member_repository.find_by_id(CastMemberId(data['id']))
        output = CastMemberOutput.from_entity(cast_member_updated) # type: ignore
        serialized = CastMemberController.serialize(output)
        assert response.content == JSONRenderer().render(serialized) # type: ignore
        assert response.data == { # type: ignore
            'data': {
                'name': response_body.get('name', cast_member_updated.name), # type: ignore
                'type': response_body.get('type', cast_member_updated.type), # type: ignore
                'id': entity.cast_member_id.id,
                'created_at': serialized['data']['created_at'],
            }
        }


@pytest.mark.django_db
@pytest.mark.group('e2e')
class TestCastMembersDeleteE2E:

    client_http: APIClient
    cast_member_repository: ICastMemberRepository
    cast_member_controller: CastMemberController

    def setup_method(self):
        self.client_http = APIClient()
        self.cast_member_repository = container.cast_member.cast_member_repository_django_orm()

    def test_invalid_request(self):
        arrange = [
            {
                'id': 'e526ad81-a291-485b-808b-91d67716db3f',
                'expected': {
                    'status_code': 404,
                    'content': {'message': "CastMember with id e526ad81-a291-485b-808b-91d67716db3f not found"}
                }
            },
            {
                'id': 'fake id',
                'expected': {
                    'status_code': 422,
                    'content': [
                        {"id": [
                            "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `k` at 3"
                        ]}]
                }
            }
        ]

        for item in arrange:
            response = self.client_http.delete(
                f'/cast-members/{item["id"]}/', format='json')
            # type: ignore
            assert response.status_code == item['expected']['status_code'] # type: ignore
            assert response.content == JSONRenderer().render(  # type: ignore
                item['expected']['content'])

    def test_delete_method(self):
        cast_member_created = CastMember.fake().a_director().build()
        self.cast_member_repository.insert(cast_member_created)
        response = self.client_http.delete(
            f'/cast-members/{cast_member_created.cast_member_id.id}/', format='json')
        assert response.status_code == 204  # type: ignore

        assert self.cast_member_repository.find_by_id(
            cast_member_created.cast_member_id) is None
