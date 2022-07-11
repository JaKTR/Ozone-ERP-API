from __future__ import annotations

import datetime
import secrets
from typing import Any, Dict, cast, List

import jwt
from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from mongoengine import BinaryField, StringField, ReferenceField, DoesNotExist, EmailField, IntField

from common import functions
from common.azure import Secrets
from common.database.common import DatabaseDocument
from identity_access_management.exceptions import (SamePasswordReusedException,
                                                   UnauthorizedRequestException,
                                                   UniqueDocumentNotFoundException)
from identity_access_management.models import constants
from identity_access_management.models.constants import PBKDF2_ALGORITHM, SUPER_ADMIN_ROLE, SECURE_STRING_LENGTH


class Role(DatabaseDocument):
    role: str = StringField(primary_key=True)
    name: str = StringField(required=True)

    @staticmethod
    def get_by_role(role: str) -> "Role":
        try:
            return cast(Role, Role.objects.get(role=role))
        except DoesNotExist:
            raise UniqueDocumentNotFoundException(f"Role not found", role)

    @staticmethod
    def is_authorized(role: str, authorized_roles: List[str] = None) -> bool:
        if authorized_roles is None:
            authorized_roles = [SUPER_ADMIN_ROLE]
        else:
            authorized_roles.append(SUPER_ADMIN_ROLE)

        return role in authorized_roles


class User(DatabaseDocument):
    username: str = StringField(primary_key=True)
    first_name: str = StringField(required=True)
    last_name: str = StringField(required=True)
    email: str = EmailField(required=True)
    organization_id: str = StringField(required=True)
    mobile: int = IntField(required=True)
    role: str = ReferenceField(Role)
    _password_hash: bytes = BinaryField(required=True)
    _password_salt: bytes = BinaryField(required=True)

    def __init__(self, *args: Any, **kwargs: Any):
        if "_password_hash" not in kwargs and "_password_salt" not in kwargs:
            kwargs["_password_salt"] = secrets.token_bytes(nbytes=constants.SALT_BYTES)
            kwargs["_password_hash"] = User.generate_hash(functions.get_secure_random_alphanumeric_string(SECURE_STRING_LENGTH), cast(bytes, kwargs["_password_salt"]))
        super().__init__(*args, **kwargs)

    def save_new_password(self, password: str) -> "User":
        if self.is_saved and self.is_password_correct(password):
            raise SamePasswordReusedException("Same password is reused")

        self._password_salt = secrets.token_bytes(nbytes=constants.SALT_BYTES)
        self._password_hash = User.generate_hash(password, self._password_salt)
        return self.save()

    def get_authorization_token(self) -> str:
        data: Dict[str, Any] = {
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
                minutes=constants.AUTHORIZATION_TOKEN_EXPIRY_MINUTES),
            User.__name__: self.get_json()
        }
        return str(jwt.encode(data, Secrets.get_private_key(),  # type: ignore[arg-type]
                              algorithm=PBKDF2_ALGORITHM))

    @staticmethod
    def get_user_from_authorization_token(authorization_token: str) -> "User":
        data: Dict[str, Any] = cast(Dict[str, Any], User.get_data_from_authorization_token(authorization_token))
        return User(**data.get(User.__name__))

    @staticmethod
    def get_data_from_authorization_token(authorization_token: str) -> Any:
        try:
            return jwt.decode(authorization_token, Secrets.get_application_public_key(),  # type: ignore[arg-type]
                              algorithms=[PBKDF2_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise UnauthorizedRequestException("Token expired", {"authorization_token": authorization_token})

    @staticmethod
    def get_by_username(username: str) -> "User":
        try:
            return cast(User, User.objects.get(username=username))
        except DoesNotExist:
            raise UniqueDocumentNotFoundException(f"Username not found", username)

    def is_password_correct(self, password: str) -> bool:
        return self.verify_hash(password, self._password_hash, self._password_salt)

    @staticmethod
    def generate_hash(password: str, salt: bytes) -> bytes:
        return PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=constants.DERIVED_KEY_LENGTH,
            salt=salt,
            iterations=constants.PBKDF2_ITERATIONS).derive(str.encode(password + User.get_password_pepper()))

    @staticmethod
    def verify_hash(password: str, password_hash: bytes, password_salt: bytes) -> bool:
        try:
            PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=constants.DERIVED_KEY_LENGTH,
                salt=password_salt,
                iterations=constants.PBKDF2_ITERATIONS).verify(str(password + User.get_password_pepper()).encode(),
                                                               password_hash)
            return True
        except InvalidKey:
            return False

    @staticmethod
    def get_password_pepper() -> str:
        return Secrets.get_secret(constants.PEPPER_KEY)
