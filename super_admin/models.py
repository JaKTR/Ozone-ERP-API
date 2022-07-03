from typing import List

from cryptography.hazmat.primitives._serialization import Encoding, PrivateFormat, NoEncryption, PublicFormat
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPrivateKeyWithSerialization

from common.azure import Secrets, Storage
from common.constants import APPLICATION_KEY_SECRET_NAME, RSA_KEY_SIZE, PUBLIC_KEY_FILE_NAME, \
    AZURE_STORAGE_PUBLIC_CONTAINER_NAME
from common.exceptions import SecretNotAvailableException, FileNotAvailableException
from common.models import ResponseModel
from identity_access_management.models import database
from identity_access_management.models.constants import SUPER_ADMIN_ROLE


class Initialization(ResponseModel):
    initialized_tasks: List[str] = []

    @staticmethod
    def initialize() -> "Initialization":
        initialization: Initialization = Initialization()

        initialization.initialize_role()
        initialization.initialize_private_key()
        initialization.initialize_public_key()

        return initialization

    def initialize_role(self) -> None:
        if len(database.Role.objects(role=SUPER_ADMIN_ROLE)) == 0:
            database.Role(role=SUPER_ADMIN_ROLE).save()
            self.initialized_tasks.append("Role")

    def initialize_private_key(self) -> None:
        def create_private_key() -> None:
            private_key: RSAPrivateKeyWithSerialization = rsa.generate_private_key(public_exponent=65537, key_size=RSA_KEY_SIZE)
            Secrets.set_secret(APPLICATION_KEY_SECRET_NAME, private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode("UTF-8"))
            self.initialized_tasks.append("Private Key")
            self.initialize_public_key(private_key)

        try:
            Secrets.get_private_key()
        except ValueError:
            create_private_key()
        except SecretNotAvailableException:
            return create_private_key()

    def initialize_public_key(self, private_key: RSAPrivateKey = None) -> None:
        def set_public_key(private_key: RSAPrivateKey = None) -> None:
            if private_key is None:
                private_key = Secrets.get_private_key()
            Storage.get_url_after_uploading_to_storage(private_key.public_key().public_bytes(Encoding.PEM, PublicFormat.PKCS1), PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
            Secrets.get_application_public_key.cache_clear()
            self.initialized_tasks.append("Public Key")

        if private_key is not None:
            set_public_key(private_key)
            return

        try:
            Secrets.get_application_public_key()
            if Secrets.get_public_key_string(Secrets.get_private_key().public_key()) != Secrets.get_public_key_string():
                set_public_key()
                return
        except ValueError:
            set_public_key()
            return
        except SecretNotAvailableException:
            set_public_key()
        except FileNotAvailableException:
            set_public_key()
