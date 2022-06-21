from typing import Any

from starlette import status


class UmbrellaException(Exception):
    pass


class ClientException(UmbrellaException):
    error_message: str
    parameters: Any
    return_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, error_message: str, parameters: Any = None, custom_return_code: int = None):
        self.error_message = error_message
        self.parameters = parameters
        self.return_code = custom_return_code if custom_return_code is not None else self.return_code
