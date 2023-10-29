from typing import Callable
from dataclasses import dataclass
from django_app.category_app.presenters import CategoryCollectionPresenter, CategoryPresenter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request as DrfRequest
from rest_framework import status as http

from core.category.application.use_cases import (
    CategoryOutput,
    CreateCategoryUseCase,
    DeleteCategoryUseCase,
    GetCategoryUseCase,
    ListCategoriesUseCase,
    UpdateCategoryUseCase
)


@dataclass(slots=True)
class CategoryController(APIView):

    create_use_case: Callable[[], CreateCategoryUseCase]
    list_use_case: Callable[[], ListCategoriesUseCase]
    get_use_case: Callable[[], GetCategoryUseCase]
    update_use_case: Callable[[], UpdateCategoryUseCase]
    delete_use_case: Callable[[], DeleteCategoryUseCase]

    def post(self, request: DrfRequest):

        input_param = CreateCategoryUseCase.Input(
            **request.data)  # type: ignore
        output = self.create_use_case().execute(input_param)
        body = CategoryController.serialize(output)
        return Response(body, status=http.HTTP_201_CREATED)

    def get(self, request: DrfRequest, category_id: str | None = None):  # pylint: disable=redefined-builtin,invalid-name
        if category_id:
            return self.get_object(category_id)

        input_param = ListCategoriesUseCase.Input(
            **request.query_params.dict()  # type: ignore
        )
        output = self.list_use_case().execute(input_param)
        data = CategoryCollectionPresenter(output=output).serialize()
        return Response(data)

    def get_object(self, category_id: str):
        input_param = GetCategoryUseCase.Input(id=category_id)  # type: ignore
        output = self.get_use_case().execute(input_param)
        body = CategoryController.serialize(output)
        return Response(body)

    def patch(self, request: DrfRequest, category_id: str):
        input_param = UpdateCategoryUseCase.Input(
            id=category_id,
            **request.data  # type: ignore
        )
        output = self.update_use_case().execute(input_param)
        body = CategoryController.serialize(output)
        return Response(body)

    def delete(self, _request: DrfRequest, category_id: str):
        input_param = DeleteCategoryUseCase.Input(
            id=category_id)  # type: ignore
        self.delete_use_case().execute(input_param)
        return Response(status=http.HTTP_204_NO_CONTENT)

    @staticmethod
    def serialize(output: CategoryOutput):
        return CategoryPresenter.from_output(output).serialize()
