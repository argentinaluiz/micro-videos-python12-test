import ast
from django.http import HttpRequest


def parse_complex_query_params(request: HttpRequest):
    complex_params = [
        param for param in request.GET if '{' in request.GET[param]]

    for param in complex_params:
        value = ast.literal_eval(request.GET[param])  # type: ignore
        request.GET = request.GET.copy()
        request.GET[param] = value

    return request
