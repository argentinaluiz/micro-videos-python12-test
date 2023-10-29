from typing import Callable
from dataclasses import dataclass
from core.cast_member.domain.repositories import CastMemberFilter
from django_app.cast_member_app.presenters import CastMemberCollectionPresenter, CastMemberPresenter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request as DrfRequest
from rest_framework import status as http

from core.cast_member.application.use_cases import (
    CastMemberOutput,
    CreateCastMemberUseCase,
    DeleteCastMemberUseCase,
    GetCastMemberUseCase,
    ListCastMembersUseCase,
    UpdateCastMemberUseCase
)


@dataclass(slots=True)
class CastMemberController(APIView):

    create_use_case: Callable[[], CreateCastMemberUseCase]
    list_use_case: Callable[[], ListCastMembersUseCase]
    get_use_case: Callable[[], GetCastMemberUseCase]
    update_use_case: Callable[[], UpdateCastMemberUseCase]
    delete_use_case: Callable[[], DeleteCastMemberUseCase]

    def post(self, request: DrfRequest):

        input_param = CreateCastMemberUseCase.Input(
            **request.data)  # type: ignore
        output = self.create_use_case().execute(input_param)
        body = CastMemberController.serialize(output)
        return Response(body, status=http.HTTP_201_CREATED)

    def get(self, request: DrfRequest, cast_member_id: str | None = None):  # pylint: disable=redefined-builtin,invalid-name
        if cast_member_id:
            return self.get_object(cast_member_id)

        query_params = request.query_params.dict()
        filter_param = query_params.pop('filter', {})
        filter_param = filter_param if isinstance(filter_param, dict) else None
        input_param = ListCastMembersUseCase.Input(
            **query_params,  # type: ignore
            filter=CastMemberFilter(
                name=filter_param.get('name'),
                type=filter_param.get('type')
            ) if filter_param else None
        )
        output = self.list_use_case().execute(input_param)
        data = CastMemberCollectionPresenter(output=output).serialize()
        return Response(data)

    def get_object(self, cast_member_id: str):
        input_param = GetCastMemberUseCase.Input(
            id=cast_member_id)  # type: ignore
        output = self.get_use_case().execute(input_param)
        body = CastMemberController.serialize(output)
        return Response(body)

    def patch(self, request: DrfRequest, cast_member_id: str):
        input_param = UpdateCastMemberUseCase.Input(
            id=cast_member_id,
            **request.data  # type: ignore
        )
        output = self.update_use_case().execute(input_param)
        body = CastMemberController.serialize(output)
        return Response(body)

    def delete(self, _request: DrfRequest, cast_member_id: str):
        input_param = DeleteCastMemberUseCase.Input(
            id=cast_member_id)  # type: ignore
        self.delete_use_case().execute(input_param)
        return Response(status=http.HTTP_204_NO_CONTENT)

    @staticmethod
    def serialize(output: CastMemberOutput):
        return CastMemberPresenter.from_output(output).serialize()
