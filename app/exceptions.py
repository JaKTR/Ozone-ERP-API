from typing import Any

from starlette import status


class UmbrellaException(Exception):
    error_message: str
    parameters: Any

    def __init__(self, error_message: str, parameters: Any = None):
        self.error_message = error_message
        self.parameters = parameters



class ClientException(UmbrellaException):
    return_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, error_message: str, parameters: Any = None, custom_return_code: int = None):
        super().__init__(error_message, parameters)
        self.return_code = custom_return_code if custom_return_code is not None else self.return_code


class ServerException(UmbrellaException):
    pass


class SecretNotAvailableException(ServerException):

    def __init__(self, parameters: Any):
        super().__init__("Secret cannot be found", parameters)

class FileNotAvailableException(ServerException):

    def __init__(self, parameters: Any):
        super().__init__("File cannot be found", parameters)