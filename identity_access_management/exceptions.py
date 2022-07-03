from typing import Any

from starlette import status

from common.exceptions import ClientException


class UniqueDocumentNotFoundException(ClientException):
    pass


class SamePasswordReusedException(ClientException):
    pass


class UnauthorizedRequestException(ClientException):

    def __init__(self, message: str, parameters: Any = None):
        super().__init__(message, parameters, status.HTTP_401_UNAUTHORIZED)
