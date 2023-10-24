from django_app.shared_app.helpers import parse_complex_query_params


class ComplexQueryParamMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request = parse_complex_query_params(request)
        return self.get_response(request)