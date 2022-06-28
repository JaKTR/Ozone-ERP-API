from typing import Any

from starlette import status

from app.exceptions import ClientException


class UniqueDocumentNotFoundException(ClientException):
    pass


class SamePasswordReusedException(ClientException):
    pass


class UnauthorizedRequestException(ClientException):

    def __init__(self, parameters: Any = None):
        super().__init__("Unauthorized login", parameters, status.HTTP_401_UNAUTHORIZED)
