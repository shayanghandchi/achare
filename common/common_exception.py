from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler
from typing import Union

from django.http import JsonResponse
from user.exceptions import AuthenticationError


class CustomResponse(JsonResponse):
    def __init__(
        self,
        *,
        data: Union[str, dict, bool] = None,
        message: Union[str, None] = None,
        error: Union[str, None, list] = None,
        status: int = status.HTTP_200_OK,
        **kwargs
    ):
        super(CustomResponse, self).__init__(
            data={
                "error": error,
            },
            status=status,
            **kwargs
        )


def base_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, AuthenticationError):
        return CustomResponse(
            error="Authorization is not provided or is not valid.",
            status=status.HTTP_401_UNAUTHORIZED,
        )
    return response
