from typing import Any, Dict, List
from urllib.parse import urlencode
from core.category.application.use_cases import CategoryOutput
from core.category.domain.entities import Category
from core.category.domain.repositories import ICategoryRepository
from core.shared.domain.exceptions import EntityValidationException, NotFoundException
from core.shared.domain.value_objects import Uuid
from django_app.category_app.api import CategoryController
from django_app.tests.category_app.fixtures import CreateCategoryApiFixture, GetObjectCategoryApiFixture, ListCategoriesApiFixture, UpdateCategoryApiFixture
from django_app.tests.shared.helpers import make_request
from pydantic import ValidationError
import pytest
from django_app.ioc_app.containers import container


@pytest.mark.django_db
class TestCategoryControllerPostMethodInt:

    controller: CategoryController
    repo: ICategoryRepository

    def setup_method(self):
        self.repo = container.category.category_repository_django_orm()
        self.controller = CategoryController(**{
            **init_category_resource_all_none(),  # type: ignore
            'create_use_case': container.category.create_category_use_case,
        })

    @pytest.mark.parametrize('request_body, exception', CreateCategoryApiFixture.arrange_for_invalid_requests())
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

    @pytest.mark.parametrize('request_body, exception', CreateCategoryApiFixture.arrange_for_entity_validation_error())
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

    @pytest.mark.parametrize('request_body, response_body', CreateCategoryApiFixture.arrange_for_create())
    def test_post_method(self, request_body: Dict[str, Any], response_body: Dict[str, Any]):
        request = make_request(
            http_method='post', send_data=request_body)
        response = self.controller.post(request)
        response_data: Dict[str, Any] = response.data  # type: ignore
        assert response.status_code == 201
        assert 'data' in response_data
        assert CreateCategoryApiFixture.keys_in_response() == list(
            response_data['data'].keys())

        data = response_data['data']
        category_created = self.repo.find_by_id(Uuid(data['id']))
        assert category_created is not None
        output = CategoryOutput.from_entity(category_created)
        serialized = CategoryController.serialize(output)

        assert response.data == serialized  # type: ignore
        assert response.data == {  # type: ignore
            'data': {
                **response_body,
                'id': category_created.category_id.id,
                'created_at': serialized['data']['created_at']
            }
        }


@pytest.mark.django_db
class TestCategoryControllerGetObjectMethodInt:

    controller: CategoryController
    repo: ICategoryRepository

    def setup_method(self):
        self.repo = container.category.category_repository_django_orm()
        self.controller = CategoryController(**{
            **init_category_resource_all_none(),  # type: ignore
            'get_use_case': container.category.get_category_use_case
        })

    def test_throw_exception_when_uuid_is_invalid(self):
        with pytest.raises(ValidationError) as assert_exception:
            self.controller.get_object('fake api')
        assert len(assert_exception.value.errors()) == 1
        assert assert_exception.value.errors()[0]['type'] == 'uuid_parsing'

    def test_throw_exception_when_category_not_found(self):
        uuid_value = 'af46842e-027d-4c91-b259-3a3642144ba4'
        with pytest.raises(NotFoundException):
            self.controller.get_object(uuid_value)

    def test_get_object_method(self):
        category = Category.fake().a_category().build()
        self.repo.insert(category)

        response = self.controller.get_object(category.category_id.id)

        assert response.status_code == 200
        response_data: Dict[str, Any] = response.data  # type: ignore
        assert 'data' in response_data
        output = CategoryOutput.from_entity(category)
        serialized = CategoryController.serialize(output)
        assert GetObjectCategoryApiFixture.keys_in_category_response() == list(
            response_data['data'].keys())
        assert response.data == serialized  # type: ignore

        assert response_data == {
            'data': {
                'id': category.category_id.id,
                'name': category.name,
                'description': category.description,
                'is_active': category.is_active,
                'created_at': serialized['data']['created_at']
            }
        }


@pytest.mark.django_db
class TestCategoryControllerGetMethodInt:

    resource: CategoryController
    repo: ICategoryRepository

    def setup_method(self):
        self.repo = container.category.category_repository_django_orm()
        self.resource = CategoryController(**{
            **init_category_resource_all_none(),  # type: ignore
            'list_use_case': container.category.list_categories_use_case
        })

    @pytest.mark.parametrize(
        'request_query_params, expected_entities, expected_meta, entities',
        ListCategoriesApiFixture.arrange_incremented_with_created_at()
    )
    def test_execute_using_empty_search_params(self,
                                               request_query_params: Dict[str, Any],
                                               expected_entities: List[Category],
                                               expected_meta: Dict[str, Any],
                                               entities: List[Category]):
        self.repo.bulk_insert(entities)
        self.assert_response(request_query_params,
                             expected_entities, expected_meta)

    @pytest.mark.parametrize(
        'request_query_params, expected_entities, expected_meta, entities',
        ListCategoriesApiFixture.arrange_unsorted()
    )
    def test_execute_using_pagination_and_sort_and_filter(self,
                                                          request_query_params: Dict[str, Any],
                                                          expected_entities: List[Category],
                                                          expected_meta: Dict[str, Any],
                                                          entities: List[Category]):
        self.repo.bulk_insert(entities)
        self.assert_response(request_query_params,
                             expected_entities, expected_meta)

    def assert_response(self, send_data: Dict[str, Any], expected_entities: List[Category], expected_meta: Dict[str, Any]):
        request = make_request(
            http_method='get',
            url=f'/?{urlencode(send_data)}'
        )
        response = self.resource.get(request)

        assert response.status_code == 200
        assert response.data == {  # type: ignore
            'data': [self.serialize_category(category) for category in expected_entities],
            'meta': expected_meta,
        }

    def serialize_category(self, category: Category):
        output = CategoryOutput.from_entity(category)
        return CategoryController.serialize(output)['data']


@pytest.mark.django_db
class TestCategoryControllerPutMethodInt:

    controller: CategoryController
    repo: ICategoryRepository

    def setup_method(self):
        self.repo = container.category.category_repository_django_orm()
        self.controller = CategoryController(**{
            **init_category_resource_all_none(),  # type: ignore
            'update_use_case': container.category.update_category_use_case
        })

    @pytest.mark.parametrize('request_body, exception', UpdateCategoryApiFixture.arrange_for_invalid_requests())
    def test_invalid_request(self, request_body: Dict[str, Any], exception: ValidationError):
        category = Category.fake().a_category().build()
        self.repo.insert(category)
        request = make_request(
            http_method='patch', send_data=request_body)
        with pytest.raises(ValidationError) as assert_exception:
            self.controller.patch(request, category.category_id.id)
        assert len(assert_exception.value.errors()) == len(exception.errors())
        # sourcery skip: no-loop-in-tests
        for assert_error, error in zip(assert_exception.value.errors(), exception.errors()):
            assert assert_error['type'] == error['type']
            assert assert_error['msg'] == error['msg']
            assert assert_error['loc'] == error['loc']

    @pytest.mark.parametrize('request_body, exception', UpdateCategoryApiFixture.arrange_for_entity_validation_error())
    def test_entity_validation_error(self, request_body: Dict[str, Any], exception: EntityValidationException):
        category = Category.fake().a_category().build()
        self.repo.insert(category)
        request = make_request(
            http_method='patch', send_data=request_body)
        with pytest.raises(EntityValidationException) as assert_exception:
            self.controller.patch(request, category.category_id.id)
        assert len(assert_exception.value.errors) == len(exception.errors)
        # sourcery skip: no-loop-in-tests
        for assert_error, expected_error in zip(assert_exception.value.errors, exception.errors):
            assert type(assert_error) is type(expected_error)

            # sourcery skip: no-conditionals-in-tests
            if isinstance(expected_error, ValidationError):
                assert len(assert_error.errors()) == len(  # type: ignore
                    expected_error.errors())

                for assert_error, expected_error in zip(
                    assert_error.errors(),  # type: ignore
                    expected_error.errors()
                ):
                    assert assert_error['type'] == expected_error['type']
                    assert assert_error['msg'] == expected_error['msg']
                    assert assert_error['loc'] == expected_error['loc']

            if isinstance(expected_error, str):  # sourcery skip: no-conditionals-in-tests
                assert assert_error == expected_error

    def test_throw_exception_when_uuid_is_invalid(self):
        request = make_request(http_method='patch', send_data={})
        with pytest.raises(ValidationError) as assert_exception:
            self.controller.patch(request, 'fake api')
        assert assert_exception.value.errors()[0]['type'] == 'uuid_parsing'

    def test_throw_exception_when_category_not_found(self):
        uuid_value = 'af46842e-027d-4c91-b259-3a3642144ba4'
        request = make_request(http_method='patch', send_data={'name': 'test'})
        with pytest.raises(NotFoundException):
            self.controller.patch(request, uuid_value)

    @pytest.mark.parametrize('request_body, response_body, entity', UpdateCategoryApiFixture.arrange_for_update())
    def test_put_method(self,
                        request_body: Dict[str, Any],
                        response_body: Dict[str, Any],
                        entity: Category):
        self.repo.insert(entity)
        request = make_request(
            http_method='put', send_data=request_body)
        response = self.controller.patch(request, entity.category_id.id)

        response_data: Dict[str, Any] = response.data  # type: ignore
        assert response.status_code == 200
        assert 'data' in response_data
        assert CreateCategoryApiFixture.keys_in_response() == list(
            response_data['data'].keys())

        data = response_data['data']
        category_updated = self.repo.find_by_id(Uuid(data['id']))
        assert category_updated is not None
        output = CategoryOutput.from_entity(category_updated)
        serialized = CategoryController.serialize(output)

        assert response.data == serialized  # type: ignore
        assert response.data == {  # type: ignore
            'data': {
                'id': category_updated.category_id.id,
                'name': response_body.get('name', category_updated.name),
                'description': response_body.get(
                    'description', category_updated.description
                ),
                'is_active': response_body.get(
                    'is_active', category_updated.is_active
                ),
                'created_at': serialized['data']['created_at'],
            }
        }


@pytest.mark.django_db
class TestCategoryControllerDeleteMethodInt:

    resource: CategoryController
    repo: ICategoryRepository

    def setup_class(self):
        self.repo = container.category.category_repository_django_orm()
        self.resource = CategoryController(**{
            **init_category_resource_all_none(),  # type: ignore
            'delete_use_case': container.category.delete_category_use_case
        })

    def test_throw_exception_when_uuid_is_invalid(self):
        request = make_request(http_method='delete')
        with pytest.raises(ValidationError) as assert_exception:
            self.resource.delete(request, 'fake api')
        assert len(assert_exception.value.errors()) == 1
        assert assert_exception.value.errors()[0]['type'] == 'uuid_parsing'

    def test_throw_exception_when_category_not_found(self):
        uuid_value = 'af46842e-027d-4c91-b259-3a3642144ba4'
        request = make_request(http_method='delete')
        with pytest.raises(NotFoundException):
            self.resource.delete(request, uuid_value)

    def test_delete_method(self):
        category = Category.fake().a_category().build()
        self.repo.insert(category)
        request = make_request(http_method='delete')
        response = self.resource.delete(request, category.category_id.id)

        assert response.status_code == 204
        assert self.repo.find_by_id(category.category_id) is None


def init_category_resource_all_none():
    return {
        'list_use_case': None,
        'get_use_case': None,
        'create_use_case': None,
        'update_use_case': None,
        'delete_use_case': None,
    }
