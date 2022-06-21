import os
import typing
from typing import Tuple, Any, Dict

from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from mongoengine import StringField, BinaryField, QuerySet

from app.authorization.exceptions import UsernameNotFoundException, SamePasswordReusedException
from app.authorization.models import constants
from app.database.common import DatabaseDocument


class Authentication(DatabaseDocument):
    username: str = StringField(primary_key=True)
    password_hash: bytes = BinaryField()
    password_salt: bytes = BinaryField()

    def __init__(self, username: str, *args: Tuple[Any], **kwargs: Dict[str, Any]):
        super().__init__(*args, **kwargs)
        self.username = username

    def save_new_password(self, password: str) -> None:
        if self.is_saved() and self.is_password_correct(password):
            raise SamePasswordReusedException("Same password is reused")

        self.password_salt = Authentication.generate_salt()
        self.password_hash = Authentication.generate_hash(password, self.password_salt)
        self.save()

    @classmethod
    def get_by_username(cls, username: str) -> "Authentication":
        query_set: QuerySet = Authentication.objects(username=username)
        if len(query_set) == 1:
            return typing.cast(Authentication, query_set.get(0))
        else:
            raise UsernameNotFoundException(f"Username not found", username)

    def is_password_correct(self, password: str) -> bool:
        return self.verify_hash(password, self.password_hash, self.password_salt)

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
