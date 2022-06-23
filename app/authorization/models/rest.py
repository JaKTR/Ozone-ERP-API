import datetime

from app.authorization.exceptions import UniqueDocumentNotFoundException, UnauthorizedLoginException
from app.authorization.models import database
from app.common import ResponseModel


class Authentication(ResponseModel):
    username: str
    password: str

    def save(self) -> None:
        try:
            database.Authentication.get_by_username(self.username).save_new_password(self.password)
        except UniqueDocumentNotFoundException as e:
            database.Authentication(self.username).save_new_password(self.password)

    def get_authentication_token(self) -> "AuthenticationToken":
        unauthorized_exception: UnauthorizedLoginException = UnauthorizedLoginException("Incorrect username and password combination", {"username": self.username})

        try:
            authentication: database.Authentication = database.Authentication.get_by_username(self.username)
            if authentication.is_password_correct(self.password):
                return AuthenticationToken(**authentication.get_authentication_token().get_json())
            else:
                raise unauthorized_exception
        except UniqueDocumentNotFoundException as e:
            raise unauthorized_exception

class AuthenticationToken(ResponseModel):
    authentication_token: str
    expiry: datetime.datetime
