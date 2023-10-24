from typing import Any
from django_app.shared_app.helpers import parse_complex_query_params
from rest_framework.request import Request as DrfRequest
from rest_framework.test import APIRequestFactory
from django.http.request import HttpRequest


def make_request(http_method: str, url: str = '/', send_data: Any = None) -> DrfRequest:
    request_factory = APIRequestFactory()
    http_method_func = getattr(request_factory, http_method)
    http_request: HttpRequest = http_method_func(url)
    request = parse_complex_query_params(http_request)
    request = DrfRequest(http_request)
    request._full_data = send_data  # pylint: disable=protected-access #type: ignore
    return request
