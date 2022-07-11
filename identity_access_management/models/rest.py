from typing import Dict, Any, List

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
            user_dict: Dict[str, Any] = self.get_dict()
            user_dict["role"] = database.Role.get_by_role(self.role)

            updated_user = database.User.get_by_username(self.username)
            updated_user.modify(**user_dict)
        except UniqueDocumentNotFoundException:
            updated_user = database.User(**self.get_dict()).save()

        return User(**updated_user.get_json())

    @staticmethod
    def get_by_username(username: str) -> "User":
        return User(**database.User.get_by_username(username).get_json())

    @staticmethod
    def get_all() -> List["User"]:
        all_users_list: List["User"] = []

        for user in database.User.get_all():
            all_users_list.append(User(**user.get_json()))

        return all_users_list


class Role(ResponseModel):
    role: str
    name: str

    def save(self) -> "Role":
        return Role(**database.Role(**self.get_dict()).save().get_json())

    @staticmethod
    def get_by_role(role: str) -> "Role":
        return Role(**database.Role.get_by_role(role).get_json())
