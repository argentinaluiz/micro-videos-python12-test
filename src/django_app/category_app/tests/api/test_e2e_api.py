from urllib.parse import urlencode
from core.category.application.use_cases import CategoryOutput
from core.category.domain.entities import Category, CategoryId
from core.category.domain.repositories import ICategoryRepository
from core.shared.domain.exceptions import EntityValidationException
from django_app.category_app.api import CategoryController
from django_app.category_app.tests.fixtures import CreateCategoryApiFixture, ListCategoriesApiFixture, UpdateCategoryApiFixture
import pytest
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIClient
from django_app.ioc_app.containers import container
from typing import Any, Dict, List
from pydantic import ValidationError


@pytest.mark.django_db
@pytest.mark.group('e2e')
class TestCategoriesPostE2E:

    client_http: APIClient
    category_repository: ICategoryRepository
    category_controller: CategoryController

    def setup_method(self):
        self.client_http = APIClient()
        self.category_repository = container.category.category_repository_django_orm()

    @pytest.mark.parametrize('request_body, exception', CreateCategoryApiFixture.arrange_for_invalid_requests())
    def test_invalid_request(self, request_body: Dict[str, Any], exception: ValidationError):
        response = self.client_http.post(
            '/categories/', data=request_body, format='json')
        assert response.status_code == 422  # type: ignore
        errors = [{error['loc'][-1]: [error['msg']]}
                  for error in exception.errors()]
        assert response.content == JSONRenderer().render(errors)  # type: ignore

    @pytest.mark.parametrize('request_body, exception', CreateCategoryApiFixture.arrange_for_entity_validation_error())
    def test_entity_validation_error(self, request_body: Dict[str, Any], exception: ValidationError):
        response = self.client_http.post(
            '/categories/', data=request_body, format='json')
        assert response.status_code == 422  # type: ignore
        errors = [{error['loc'][-1]: [error['msg']]}
                  for error in exception.errors()]
        assert response.content == JSONRenderer().render(errors)  # type: ignore

    @pytest.mark.parametrize('request_body, expected_response_body', CreateCategoryApiFixture.arrange_for_create())
    def test_post_method(self, request_body: Dict[str, Any], expected_response_body: Dict[str, Any]):
        response = self.client_http.post(
            '/categories/', data=request_body, format='json')
        assert response.status_code == 201  # type: ignore
        data = response.data['data']  # type: ignore
        assert CreateCategoryApiFixture.keys_in_response() == list(data.keys())
        category_created = self.category_repository.find_by_id(
            CategoryId(data['id']))
        output = CategoryOutput.from_entity(category_created)  # type: ignore
        serialized = CategoryController.serialize(output)
        assert response.content == JSONRenderer().render(serialized)  # type: ignore
        assert response.data == {  # type: ignore
            'data': {
                **expected_response_body,
                'id': category_created.category_id.id,  # type: ignore
                'created_at': serialized['data']['created_at'],
            }
        }


@pytest.mark.django_db
@pytest.mark.group('e2e')
class TestCategoriesGetObjectE2E:

    client_http: APIClient
    category_repository: ICategoryRepository
    category_controller: CategoryController

    def setup_method(self):
        self.client_http = APIClient()
        self.category_repository = container.category.category_repository_django_orm()

    def test_invalid_request(self):
        arrange = [
            {
                'id': 'e526ad81-a291-485b-808b-91d67716db3f',
                'expected': {
                    'status_code': 404,
                    'content': {'message': "Category with id e526ad81-a291-485b-808b-91d67716db3f not found"}
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
                f'/categories/{item["id"]}/', format='json')
            assert response.status_code == item['expected']['status_code'] # type: ignore
            assert response.content == JSONRenderer().render(  # type: ignore
                item['expected']['content'])

    def test_get_object_method(self):
        category_created = Category.fake().a_category().build()
        self.category_repository.insert(category_created)
        response = self.client_http.get(
            f'/categories/{category_created.category_id.id}/', format='json')
        assert response.status_code == 200  # type: ignore
        output = CategoryOutput.from_entity(category_created)
        serialized = CategoryController.serialize(output)
        assert response.content == JSONRenderer().render(serialized)  # type: ignore


@pytest.mark.django_db
@pytest.mark.group('e2e')
class TestCategoriesGetE2E:

    client_http: APIClient
    category_repository: ICategoryRepository
    category_controller: CategoryController

    def setup_method(self):
        self.client_http = APIClient()
        self.category_repository = container.category.category_repository_django_orm()

    @pytest.mark.parametrize(
        'request_query_params, expected_entities, expected_meta, entities',
        ListCategoriesApiFixture.arrange_incremented_with_created_at()
    )
    def test_execute_using_empty_search_params(self,
                                               request_query_params: Dict[str, Any],
                                               expected_entities: List[Category],
                                               expected_meta: Dict[str, Any],
                                               entities: List[Category]):
        self.category_repository.bulk_insert(entities)
        self.assert_response(request_query_params,
                             expected_entities, expected_meta)

    @pytest.mark.parametrize(
        'request_query_params, expected_entities, expected_meta, entities',
        ListCategoriesApiFixture.arrange_unsorted())
    def test_execute_using_pagination_and_sort_and_filter(self, request_query_params: Dict[str, Any],
                                                          expected_entities: List[Category],
                                                          expected_meta: Dict[str, Any],
                                                          entities: List[Category]):
        self.category_repository.bulk_insert(entities)
        self.assert_response(request_query_params,
                             expected_entities, expected_meta)

    def assert_response(self, send_data: dict, entities: List[Category], expected_meta: Dict[str, Any]):
        response = self.client_http.get(
            f'/categories/?{urlencode(send_data)}', format='json')

        assert response.status_code == 200  # type: ignore
        assert response.data == {  # type: ignore
            'data': [self.serialize_category(category) for category in entities],
            'meta': expected_meta,
        }

    def serialize_category(self, category: Category):
        output = CategoryOutput.from_entity(category)
        return CategoryController.serialize(output)['data']


@pytest.mark.django_db
@pytest.mark.group('e2e')
class TestCategoriesPatchE2E:

    client_http: APIClient
    category_repository: ICategoryRepository
    category_resource: CategoryController

    def setup_method(self):
        self.client_http = APIClient()
        self.category_repository = container.category.category_repository_django_orm()

    @pytest.mark.parametrize('request_body, exception', UpdateCategoryApiFixture.arrange_for_invalid_requests())
    def test_invalid_request(self, request_body: Dict[str, Any], exception: ValidationError):
        response = self.client_http.patch(
            '/categories/e526ad81-a291-485b-808b-91d67716db3f/', data=request_body, format='json')
        assert response.status_code == 422  # type: ignore
        errors = [{error['loc'][-1]: [error['msg']]}
                  for error in exception.errors()]
        assert response.content == JSONRenderer().render(errors)  # type: ignore

    @pytest.mark.parametrize('request_body, exception', UpdateCategoryApiFixture.arrange_for_entity_validation_error())
    def test_entity_validation_error(self, request_body: Dict[str, Any], exception: EntityValidationException):
        category = Category.fake().a_category().build()
        self.category_repository.insert(category)
        response = self.client_http.patch(
            f'/categories/{category.category_id.id}/', data=request_body, format='json')
        assert response.status_code == 422  # type: ignore
        errors = [{key: error} for key, error in exception.errors.items()]
        assert response.content == JSONRenderer().render(errors)  # type: ignore

    @pytest.mark.parametrize('request_body, response_body, entity', UpdateCategoryApiFixture.arrange_for_update())
    def test_patch_method(self,
                          request_body: Dict[str, Any],
                          response_body: Dict[str, Any],
                          entity: Category):
        self.category_repository.insert(entity)
        response = self.client_http.patch(
            f'/categories/{entity.category_id.id}/', data=request_body, format='json')
        assert response.status_code == 200 # type: ignore
        assert 'data' in response.data # type: ignore
        data = response.data['data'] # type: ignore
        assert UpdateCategoryApiFixture.keys_in_response() == list(data.keys())
        category_updated = self.category_repository.find_by_id(CategoryId(data['id']))
        output = CategoryOutput.from_entity(category_updated) # type: ignore
        serialized = CategoryController.serialize(output)
        assert response.content == JSONRenderer().render(serialized) # type: ignore
        assert response.data == { # type: ignore
            'data': {
                'name': response_body.get('name', category_updated.name), # type: ignore
                'description': response_body.get('description', category_updated.description), # type: ignore
                'is_active': response_body.get('is_active', category_updated.is_active), # type: ignore
                'id': entity.category_id.id,
                'created_at': serialized['data']['created_at'],
            }
        }


@pytest.mark.django_db
@pytest.mark.group('e2e')
class TestCategoriesDeleteE2E:

    client_http: APIClient
    category_repository: ICategoryRepository
    category_controller: CategoryController

    def setup_method(self):
        self.client_http = APIClient()
        self.category_repository = container.category.category_repository_django_orm()

    def test_invalid_request(self):
        arrange = [
            {
                'id': 'e526ad81-a291-485b-808b-91d67716db3f',
                'expected': {
                    'status_code': 404,
                    'content': {'message': "Category with id e526ad81-a291-485b-808b-91d67716db3f not found"}
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
                f'/categories/{item["id"]}/', format='json')
            # type: ignore
            assert response.status_code == item['expected']['status_code'] # type: ignore
            assert response.content == JSONRenderer().render(  # type: ignore
                item['expected']['content'])

    def test_delete_method(self):
        category_created = Category.fake().a_category().build()
        self.category_repository.insert(category_created)
        response = self.client_http.delete(
            f'/categories/{category_created.category_id.id}/', format='json')
        assert response.status_code == 204  # type: ignore

        assert self.category_repository.find_by_id(
            category_created.category_id) is None
