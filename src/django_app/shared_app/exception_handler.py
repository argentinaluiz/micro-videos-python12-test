from typing import Any, Dict, Sequence
from core.shared.domain.exceptions import EntityValidationException, NotFoundException
from pydantic import ValidationError
from rest_framework.views import exception_handler as rest_framework_exception_handler
from rest_framework.response import Response


def handle_validation_error(exc: ValidationError, context):
    errors = [{error["loc"][-1]: [error["msg"]]} for error in exc.errors()]
    return Response(errors, 422)


def handle_entity_validation_error(exc: EntityValidationException, context):
    errors = []

    for key, error in exc.errors.items():
        if isinstance(error, list):
            errors.append({
                key: error
            })
        else:
            errors.append(error)

    return Response(errors, 422)


def handle_not_found_error(exc: NotFoundException, context):
    response = Response({'message': exc.args[0]}, 404)
    response.status_code = 404
    return response


handlers = [
    {
        'exception': ValidationError,
        'handle': handle_validation_error
    },
    {
        'exception': EntityValidationException,
        'handle': handle_entity_validation_error
    },
    {
        'exception': NotFoundException,
        'handle': handle_not_found_error
    }
]


def custom_exception_handler(exc, context):

    for handler in handlers:
        if isinstance(exc, handler['exception']):
            return handler['handle'](exc, context)

    return rest_framework_exception_handler(exc, context)
