from typing import Any

from starlette import status

from app.exceptions import ClientException


class UsernameNotFoundException(ClientException):
    pass


class SamePasswordReusedException(ClientException):
    pass


class UnauthorizedLoginException(ClientException):

    def __init__(self, error_message: str, parameters: Any = None):
        super().__init__(error_message, parameters, status.HTTP_401_UNAUTHORIZED)