

import datetime
from unittest import mock
from urllib.parse import urlencode
from uuid import UUID
from core.cast_member.application.use_cases import CastMemberOutput, CreateCastMemberUseCase, DeleteCastMemberUseCase, GetCastMemberUseCase, ListCastMembersUseCase, UpdateCastMemberUseCase
from core.cast_member.domain.entities import CastMember, CastMemberId
from core.cast_member.domain.repositories import CastMemberFilter
from django_app.cast_member_app.api import CastMemberController
from django_app.cast_member_app.tests.api.helpers import init_cast_member_controller_all_none
from django_app.shared_app.tests.helpers import make_request


class TestCastMemberControllerUnit:

    def test_serialize(self):
        output = CastMemberOutput(
            id='1',
            name='test',
            type=CastMember.DIRECTOR,
            created_at=datetime.datetime(
                2021, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        )
        body = CastMemberController.serialize(output)
        assert body == {
            'data': {
                'id': '1',
                'name': 'test',
                'type': CastMember.DIRECTOR,
                'created_at': '2021-01-01T00:00:00+00:00'
            }
        }

    def test_post(self):
        expected_response = {
            'data': {
                'id': '1',
                'name': 'test',
                'type': CastMember.DIRECTOR,
                'created_at': '2021-01-01T00:00:00+00:00'
            }
        }

        mock_create_use_case = mock.Mock(CreateCastMemberUseCase)
        mock_create_use_case.execute.return_value = CreateCastMemberUseCase.Output(  # type: ignore
            id='1',
            name='test',
            type=CastMember.DIRECTOR,
            created_at=datetime.datetime(
                2021, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        )

        controller = CastMemberController(**{
            **init_cast_member_controller_all_none(),
            'create_use_case': lambda: mock_create_use_case  # type: ignore
        })

        request = make_request('post', send_data={
            'name': 'test',
            'type': CastMember.DIRECTOR,
        })

        response = controller.post(request)

        assert response.status_code == 201
        assert response.data == expected_response  # type: ignore
        mock_create_use_case.execute.assert_called_once_with(  # type: ignore
            CreateCastMemberUseCase.Input(
                name='test',
                type=CastMember.DIRECTOR,
            )
        )

    def test_get_object(self):
        expected_response = {
            'data': {
                'id': '1',
                'name': 'test',
                'type': CastMember.DIRECTOR,
                'created_at': '2021-01-01T00:00:00+00:00'
            }
        }

        mock_get_use_case = mock.Mock(GetCastMemberUseCase)
        mock_get_use_case.execute.return_value = GetCastMemberUseCase.Output(  # type: ignore
            id='1',
            name='test',
            type=CastMember.DIRECTOR,
            created_at=datetime.datetime(
                2021, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        )

        controller = CastMemberController(**{
            **init_cast_member_controller_all_none(),
            'get_use_case': lambda: mock_get_use_case  # type: ignore
        })

        _id = CastMemberId().id

        response = controller.get_object(_id)

        assert response.status_code == 200
        assert response.data == expected_response  # type: ignore
        mock_get_use_case.execute.assert_called_once_with(  # type: ignore
            GetCastMemberUseCase.Input(
                id=UUID(_id)
            )
        )

    def test_get(self):
        expected_response = {
            'data': [
                {
                    'id': '1',
                    'name': 'test',
                    'type': CastMember.DIRECTOR,
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

        mock_list_use_case = mock.Mock(ListCastMembersUseCase)
        mock_list_use_case.execute.return_value = ListCastMembersUseCase.Output(  # type: ignore
            items=[
                CastMemberOutput(
                    id='1',
                    name='test',
                    type=CastMember.DIRECTOR,
                    created_at=datetime.datetime(
                        2021, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
                )
            ],
            total=1,
            current_page=1,
            per_page=10,
            last_page=1
        )

        controller = CastMemberController(**{
            **init_cast_member_controller_all_none(),
            'list_use_case': lambda: mock_list_use_case  # type: ignore
        })

        query_params = {
            'page': 1,
            'per_page': 10,
            'sort': 'name',
            'sort_dir': 'asc',
            'filter': {
                'name': 'test',
                'type': CastMember.DIRECTOR,
            }
        }

        request = make_request('get', f'/?{urlencode(query_params)}')

        response = controller.get(request)

        assert response.status_code == 200
        assert response.data == expected_response  # type: ignore
        mock_list_use_case.execute.assert_called_once_with(  # type: ignore
            ListCastMembersUseCase.Input(
                page=1,
                per_page=10,
                sort='name',
                sort_dir='asc',
                filter=CastMemberFilter(
                    name='test',
                    type=CastMember.DIRECTOR,
                )
            )
        )

        query_params = {
            'page': 1,
            'per_page': 10,
            'sort': 'name',
            'sort_dir': 'asc',
        }

        request = make_request('get', f'/?{urlencode(query_params)}')

        response = controller.get(request)

        assert response.status_code == 200
        assert response.data == expected_response  # type: ignore
        mock_list_use_case.execute.assert_called_with(  # type: ignore
            ListCastMembersUseCase.Input(
                page=1,
                per_page=10,
                sort='name',
                sort_dir='asc',
                filter=None
            )
        )

    def test_patch(self):
        expected_response = {
            'data': {
                'id': '1',
                'name': 'test',
                'type': CastMember.DIRECTOR,
                'created_at': '2021-01-01T00:00:00+00:00'
            }
        }

        mock_update_use_case = mock.Mock(UpdateCastMemberUseCase)
        mock_update_use_case.execute.return_value = UpdateCastMemberUseCase.Output(  # type: ignore
            id='1',
            name='test',
            type=CastMember.DIRECTOR,
            created_at=datetime.datetime(
                2021, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        )

        controller = CastMemberController(**{
            **init_cast_member_controller_all_none(),
            'update_use_case': lambda: mock_update_use_case  # type: ignore
        })

        _id = CastMemberId().id

        request = make_request('patch', send_data={
            'name': 'test',
            'type': CastMember.DIRECTOR,
        })

        response = controller.patch(request, _id)

        assert response.status_code == 200
        assert response.data == expected_response  # type: ignore
        mock_update_use_case.execute.assert_called_once_with(  # type: ignore
            UpdateCastMemberUseCase.Input(
                id=UUID(_id),
                name='test',
                type=CastMember.DIRECTOR,
            )
        )

    def test_delete(self):
        mock_delete_use_case = mock.Mock(DeleteCastMemberUseCase)
        mock_delete_use_case.execute.return_value = None  # type: ignore

        controller = CastMemberController(**{
            **init_cast_member_controller_all_none(),
            'delete_use_case': lambda: mock_delete_use_case  # type: ignore
        })

        _id = CastMemberId().id

        request = make_request('delete')

        response = controller.delete(request, _id)

        assert response.status_code == 204
        mock_delete_use_case.execute.assert_called_once_with(  # type: ignore
            DeleteCastMemberUseCase.Input(
                id=UUID(_id)
            )
        )
