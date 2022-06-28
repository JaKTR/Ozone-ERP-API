from __future__ import annotations

import datetime
import os
from typing import Any, Dict, Tuple, cast

import jwt
from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from mongoengine import BinaryField, QuerySet, StringField

from app.authentication.exceptions import (SamePasswordReusedException,
                                           UnauthorizedRequestException,
                                           UniqueDocumentNotFoundException)
from app.authentication.models import constants
from app.authentication.models.constants import PBKDF2_ALGORITHM
from app.azure import Secrets
from app.database.common import DatabaseDocument


class User(DatabaseDocument):
    username: str = StringField(primary_key=True)
    first_name: str = StringField()
    _password_hash: bytes = BinaryField()
    _password_salt: bytes = BinaryField()

    def __init__(self, username: str, *args: Tuple[Any], **kwargs: Dict[str, Any]):
        super().__init__(*args, **kwargs)
        self.username = username

    def save_new_password(self, password: str) -> "User":
        if self.is_saved() and self.is_password_correct(password):
            raise SamePasswordReusedException("Same password is reused")

        self._password_salt = User.generate_salt()
        self._password_hash = User.generate_hash(password, self._password_salt)
        return self.save()

    def get_authentication_token(self) -> str:
        data: Dict[str, Any] = {
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=constants.AUTHORIZATION_TOKEN_EXPIRY_MINUTES),
            User.__name__: self.get_json()
        }
        return str(jwt.encode(data, Secrets.get_application_private_key(), algorithm=PBKDF2_ALGORITHM))  # type: ignore[arg-type]

    @staticmethod
    def get_user_from_authentication_token(authentication_token: str) -> "User":
        data: Dict[str, Any]
        try:
            data = jwt.decode(authentication_token, Secrets.get_application_public_key(), algorithms=PBKDF2_ALGORITHM) # type: ignore[arg-type]
        except jwt.ExpiredSignatureError:
            raise UnauthorizedRequestException({"authentication_token": authentication_token})

        return User(**data.get(User.__name__))

    @staticmethod
    def get_by_username(username: str, return_new_document: bool = False) -> "User":
        query_set: QuerySet = User.objects(username=username)
        if len(query_set) == 1:
            return cast(User, query_set.get(0))
        elif return_new_document:
            return User(username)
        else:
            raise UniqueDocumentNotFoundException(f"Username not found", username)

    def is_password_correct(self, password: str) -> bool:
        return self.verify_hash(password, self._password_hash, self._password_salt)

    @staticmethod
    def generate_salt() -> bytes:
        return os.urandom(constants.SALT_LENGTH)

    @staticmethod
    def generate_hash(password: str, salt: bytes) -> bytes:
        return PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=constants.DERIVED_KEY_LENGTH,
            salt=salt,
            iterations=constants.PBKDF2_ITERATIONS).derive(str.encode(password))

    @staticmethod
    def verify_hash(password: str, password_hash: bytes, password_salt: bytes) -> bool:
        try:
            PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=constants.DERIVED_KEY_LENGTH,
                salt=password_salt,
                iterations=constants.PBKDF2_ITERATIONS).verify(str(password).encode(), password_hash)
            return True
        except InvalidKey as e:
            return False
