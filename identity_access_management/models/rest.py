from typing import Optional

from common.models import ResponseModel
from identity_access_management.exceptions import (UnauthorizedRequestException,
                                                   UniqueDocumentNotFoundException)
from identity_access_management.models import database


class Authorization(ResponseModel):
    username: str
    password: str

    def save(self) -> database.User:
        return database.User.get_by_username(self.username, True).save_new_password(self.password)

    def get_authorization_token(self) -> str:
        unauthorized_exception: UnauthorizedRequestException = UnauthorizedRequestException("Invalid credentials", {"username": self.username})

        try:
            user: database.User = database.User.get_by_username(self.username)
            if user.is_password_correct(self.password):
                return user.get_authorization_token()
            else:
                raise unauthorized_exception
        except UniqueDocumentNotFoundException:
            raise unauthorized_exception


class User(ResponseModel):
    username: str
    first_name: str
    role: str
    password: Optional[str]

    def save(self) -> "User":
        user: database.User = database.User.get_by_username(self.username) if self.password is None else Authorization(
            username=self.username, password=self.password).save()
        user.first_name = self.first_name
        user.role = database.Role.get_by_role(self.role)
        return User(**user.save().get_json())


class Role(ResponseModel):
    role: str

    def save(self) -> "Role":
        return Role(**database.Role(**self.get_dict()).save().get_json())
