

import datetime
from unittest import mock
from uuid import UUID
from core.category.application.use_cases import CategoryOutput, CreateCategoryUseCase, DeleteCategoryUseCase, GetCategoryUseCase, ListCategoriesUseCase, UpdateCategoryUseCase
from core.category.domain.entities import CategoryId
from django_app.category_app.api import CategoryController
from django_app.category_app.tests.api.helpers import init_category_resource_all_none
from django_app.shared_app.tests.helpers import make_request


class TestCategoryControllerUnit:

    def test_serialize(self):
        output = CategoryOutput(
            id='1',
            name='test',
            description='test',
            is_active=True,
            created_at=datetime.datetime(
                2021, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        )
        body = CategoryController.serialize(output)
        assert body == {
            'data': {
                'id': '1',
                'name': 'test',
                'description': 'test',
                'is_active': True,
                'created_at': '2021-01-01T00:00:00+00:00'
            }
        }

    def test_post(self):
        expected_response = {
            'data': {
                'id': '1',
                'name': 'test',
                'description': 'test',
                'is_active': True,
                'created_at': '2021-01-01T00:00:00+00:00'
            }
        }

        mock_create_use_case = mock.Mock(CreateCategoryUseCase)
        mock_create_use_case.execute.return_value = CreateCategoryUseCase.Output(  # type: ignore
            id='1',
            name='test',
            description='test',
            is_active=True,
            created_at=datetime.datetime(
                2021, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        )

        controller = CategoryController(**{
            **init_category_resource_all_none(),
            'create_use_case': lambda: mock_create_use_case  # type: ignore
        })

        request = make_request('post', send_data={
            'name': 'test',
            'description': 'test',
            'is_active': True,
        })

        response = controller.post(request)

        assert response.status_code == 201
        assert response.data == expected_response  # type: ignore
        mock_create_use_case.execute.assert_called_once_with(  # type: ignore
            CreateCategoryUseCase.Input(
                name='test',
                description='test',
                is_active=True,
            )
        )

    def test_get_object(self):
        expected_response = {
            'data': {
                'id': '1',
                'name': 'test',
                'description': 'test',
                'is_active': True,
                'created_at': '2021-01-01T00:00:00+00:00'
            }
        }

        mock_get_use_case = mock.Mock(GetCategoryUseCase)
        mock_get_use_case.execute.return_value = GetCategoryUseCase.Output(  # type: ignore
            id='1',
            name='test',
            description='test',
            is_active=True,
            created_at=datetime.datetime(
                2021, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        )

        controller = CategoryController(**{
            **init_category_resource_all_none(),
            'get_use_case': lambda: mock_get_use_case  # type: ignore
        })

        _id = CategoryId().id

        response = controller.get_object(_id)

        assert response.status_code == 200
        assert response.data == expected_response  # type: ignore
        mock_get_use_case.execute.assert_called_once_with(  # type: ignore
            GetCategoryUseCase.Input(
                id=UUID(_id)
            )
        )

    def test_get(self):
        expected_response = {
            'data': [
                {
                    'id': '1',
                    'name': 'test',
                    'description': 'test',
                    'is_active': True,
                    'created_at': '2021-01-01T00:00:00+00:00'
                }
            ],
            'meta': {
                'total': 1,
                'current_page': 1,
                'per_page': 10,
                'last_page': 1
            }
        }

        mock_list_use_case = mock.Mock(ListCategoriesUseCase)
        mock_list_use_case.execute.return_value = ListCategoriesUseCase.Output(  # type: ignore
            items=[
                CategoryOutput(
                    id='1',
                    name='test',
                    description='test',
                    is_active=True,
                    created_at=datetime.datetime(
                        2021, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
                )
            ],
            total=1,
            current_page=1,
            per_page=10,
            last_page=1
        )

        controller = CategoryController(**{
            **init_category_resource_all_none(),
            'list_use_case': lambda: mock_list_use_case  # type: ignore
        })

        request = make_request(
            'get', '/?page=1&per_page=10&sort=name&sort_dir=asc&filter=test')

        response = controller.get(request)

        assert response.status_code == 200
        assert response.data == expected_response  # type: ignore
        mock_list_use_case.execute.assert_called_once_with(  # type: ignore
            ListCategoriesUseCase.Input(
                page=1,
                per_page=10,
                sort='name',
                sort_dir='asc',
                filter='test'
            )
        )

    def test_patch(self):
        expected_response = {
            'data': {
                'id': '1',
                'name': 'test',
                'description': 'test',
                'is_active': True,
                'created_at': '2021-01-01T00:00:00+00:00'
            }
        }

        mock_update_use_case = mock.Mock(UpdateCategoryUseCase)
        mock_update_use_case.execute.return_value = UpdateCategoryUseCase.Output(  # type: ignore
            id='1',
            name='test',
            description='test',
            is_active=True,
            created_at=datetime.datetime(
                2021, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        )

        controller = CategoryController(**{
            **init_category_resource_all_none(),
            'update_use_case': lambda: mock_update_use_case  # type: ignore
        })

        _id = CategoryId().id

        request = make_request('patch', send_data={
            'name': 'test',
            'description': 'test',
            'is_active': True,
        })

        response = controller.patch(request, _id)

        assert response.status_code == 200
        assert response.data == expected_response  # type: ignore
        mock_update_use_case.execute.assert_called_once_with(  # type: ignore
            UpdateCategoryUseCase.Input(
                id=UUID(_id),
                name='test',
                description='test',
                is_active=True,
            )
        )

    def test_delete(self):
        mock_delete_use_case = mock.Mock(DeleteCategoryUseCase)
        mock_delete_use_case.execute.return_value = None  # type: ignore

        controller = CategoryController(**{
            **init_category_resource_all_none(),
            'delete_use_case': lambda: mock_delete_use_case  # type: ignore
        })

        _id = CategoryId().id

        request = make_request('delete')

        response = controller.delete(request, _id)

        assert response.status_code == 204
        mock_delete_use_case.execute.assert_called_once_with(  # type: ignore
            DeleteCategoryUseCase.Input(
                id=UUID(_id)
            )
        )
