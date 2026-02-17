import inspect
from typing import Any, Callable

from django.conf import settings
from django.utils import encoding
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    response = exception_handler(exc, context)

    if response is None:
        return None

    errors = format_drf_errors(response, context, exc)

    response.data = {'errors': errors}

    return response


def format_drf_errors(response: Response, context: dict[str, Any], exc: Exception) -> list[dict[str, Any]]:
    errors_list: list[dict[str, Any]] = []
    error_msg_gen = error_generator(response.status_code)

    if isinstance(response.data, list):
        for message in response.data:
            errors_list.append(error_msg_gen(message))

    elif isinstance(response.data, dict):
        for field, error in response.data.items():
            pointer = f'/data/{field}'

            if isinstance(error, dict):
                errors_list.append(error)
            elif isinstance(error, str | bytes):
                classes = inspect.getmembers(exceptions, inspect.isclass)
                if isinstance(exc, tuple(x[1] for x in classes)):
                    pointer = '/data'
                errors_list.append(error_msg_gen(error, pointer=pointer, label=field))
            elif isinstance(error, list):
                for message in error:
                    if isinstance(message, dict):
                        errors_list.append(error_msg_gen(
                            message.get('detail', 'Error'),
                            pointer=pointer,
                            label=message.get('label', field),
                            code=message.get('code')
                        ))
                    else:
                        error_code = getattr(message, 'code', 'invalid')
                        errors_list.append(error_msg_gen(message, pointer=pointer, label=field, code=error_code))
            else:
                errors_list.append(error_msg_gen(error, pointer=pointer, label=field))

    return errors_list


def error_generator(status_code: int) -> Callable:
    default_label = settings.REST_FRAMEWORK.get('NON_FIELD_ERRORS_KEY', 'non_field_errors')

    def generate_error(
            message: Any,
            pointer: str = '/data',
            label: str | None = None,
            code: str | None = None
    ) -> dict[str, Any]:
        return {
            'field': label or default_label,
            'detail': encoding.force_str(message),
            'source': {
                'pointer': pointer,
            },
            'status': encoding.force_str(status_code),
            'code': code or 'invalid'
        }

    return generate_error
