from __future__ import annotations

import datetime
import os
from typing import Tuple, Any, Dict, cast

import jwt
from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from mongoengine import StringField, BinaryField, QuerySet, DateTimeField

from app.authorization.exceptions import UniqueDocumentNotFoundException, SamePasswordReusedException
from app.authorization.models import constants
from app.azure import Secrets
from app.database.common import DatabaseDocument


class Authentication(DatabaseDocument):
    username: str = StringField(primary_key=True)
    _password_hash: bytes = BinaryField()
    _password_salt: bytes = BinaryField()

    def __init__(self, username: str, *args: Tuple[Any], **kwargs: Dict[str, Any]):
        super().__init__(*args, **kwargs)
        self.username = username

    def save_new_password(self, password: str) -> None:
        if self.is_saved() and self.is_password_correct(password):
            raise SamePasswordReusedException("Same password is reused")

        self._password_salt = Authentication.generate_salt()
        self._password_hash = Authentication.generate_hash(password, self._password_salt)
        self.save()

    def get_authentication_token(self) -> AuthenticationToken:
        return AuthenticationToken(self)

    @staticmethod
    def get_by_username(username: str) -> "Authentication":
        query_set: QuerySet = Authentication.objects(username=username)
        if len(query_set) == 1:
            return cast(Authentication, query_set.get(0))
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


class AuthenticationToken(DatabaseDocument):
    authentication_token: str = StringField(primary_key=True)
    expiry: datetime.datetime = DateTimeField()

    def __init__(self, authentication: Authentication, *args: Tuple[Any], **values: Dict[str, Any]):
        super().__init__(*args, **values)
        private_key: RSAPrivateKey = Secrets.get_application_private_key()
        self.expiry = datetime.datetime.now() + datetime.timedelta(minutes=constants.AUTHORIZATION_TOKEN_EXPIRY_MINUTES)
        data: Dict[str, Any] = authentication.get_json(exclude_fields=["authorization_token"])
        self.authentication_token = str(jwt.encode(data, private_key, algorithm="RS256"))  # type: ignore[arg-type]
        self.save()

    @staticmethod
    def is_authentication_token_valid(authentication_token: str) -> bool:
        try:
            return AuthenticationToken.get_by_authentication_token(authentication_token).expiry < (
                        datetime.datetime.now() + datetime.timedelta(
                    minutes=constants.AUTHORIZATION_TOKEN_EXPIRY_MINUTES))
        except UniqueDocumentNotFoundException as e:
            return False

    @staticmethod
    def get_by_authentication_token(authentication_token: str) -> "AuthenticationToken":
        query_set: QuerySet = AuthenticationToken.objects(authentication_token=authentication_token)
        if len(query_set) == 1:
            return cast(AuthenticationToken, query_set.get(0))
        else:
            raise UniqueDocumentNotFoundException(f"Authentication token not found", authentication_token)
