from common.models import ResponseModel
from identity_access_management.exceptions import (UnauthorizedRequestException,
                                                   UniqueDocumentNotFoundException)
from identity_access_management.models import database


class Authorization(ResponseModel):
    username: str
    password: str

    def save(self) -> database.User:
        return database.User.get_by_username(self.username).save_new_password(self.password)

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
    last_name: str
    email: str
    organization_id: str
    mobile: int
    role: str

    def save(self) -> "User":
        updated_user: database.User

        try:
            updated_user = database.User.get_by_username(self.username)
            updated_user.modify(self.get_dict())
        except UniqueDocumentNotFoundException:
            updated_user = database.User(**self.get_dict()).save()

        return User(**updated_user.get_json())


class Role(ResponseModel):
    role: str
    name: str

    def save(self) -> "Role":
        return Role(**database.Role(**self.get_dict()).save().get_json())
