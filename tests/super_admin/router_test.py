from typing import Dict

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPrivateKeyWithSerialization
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from requests import Response

from common.azure import Secrets, Storage
from common.constants import APPLICATION_KEY_SECRET_NAME, PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME, RSA_KEY_SIZE
from identity_access_management.models import database
from identity_access_management.models.constants import PEPPER_KEY
from super_admin import constants
from super_admin.models import Initialization
from tests.super_admin import super_admin_test_client


class TestInitialization:
    public_key_initialization_key: str = "Public Key"
    
    @classmethod
    def get_initialization_response(cls) -> Initialization:
        response: Response = super_admin_test_client.post(f"{constants.BASE_URL}{constants.INITIALIZE_URL}")
        return Initialization(**response.json())

    def test_create_super_admin_role(self) -> None:
        database.Role.drop_collection()
        assert "Role" in TestInitialization.get_initialization_response().initialized_tasks

    def test_create_default_super_admins(self) -> None:
        database.User.drop_collection()

        is_penta_found: bool = False
        is_kavindu_found: bool = False
        for task in TestInitialization.get_initialization_response().initialized_tasks:
            if isinstance(task, Dict) and "penta" in task:
                is_penta_found = True
            if isinstance(task, Dict) and "kavindu" in task:
                is_kavindu_found = True
            if is_penta_found and is_kavindu_found:
                break

        if not is_penta_found or not is_kavindu_found:
            raise AssertionError
        assert database.User.get_by_username("penta").is_saved
        assert database.User.get_by_username("kavindu").is_saved

    def test_recreate_default_super_admins(self) -> None:
        for task in TestInitialization.get_initialization_response().initialized_tasks:
            if isinstance(task, Dict) and ("penta" in task or "kavindu" in task):
                raise AssertionError

    def test_no_pepper(self) -> None:
        initial_pepper: str = database.User.get_password_pepper()
        Secrets.delete_secret(PEPPER_KEY)
        assert "Pepper" in TestInitialization.get_initialization_response().initialized_tasks
        Secrets.set_secret(PEPPER_KEY, initial_pepper)

    def test_no_private_key(self) -> None:
        Secrets.delete_secret(APPLICATION_KEY_SECRET_NAME)
        Secrets.get_private_key.cache_clear()
        assert "Private Key" in TestInitialization.get_initialization_response().initialized_tasks
        assert isinstance(Secrets.get_private_key(), RSAPrivateKey)

    def test_invalid_private_key(self) -> None:
        Secrets.set_secret(APPLICATION_KEY_SECRET_NAME, "a")
        Secrets.get_private_key.cache_clear()
        assert "Private Key" in TestInitialization.get_initialization_response().initialized_tasks
        assert isinstance(Secrets.get_private_key(), RSAPrivateKey)

    def test_no_public_key(self) -> None:
        Storage.delete_file(PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        Secrets.get_application_public_key.cache_clear()
        assert self.public_key_initialization_key in TestInitialization.get_initialization_response().initialized_tasks
        assert Secrets.get_public_key_string(Secrets.get_private_key().public_key()) == Secrets.get_public_key_string(Secrets.get_application_public_key())

    def test_invalid_public_key(self) -> None:
        Storage.get_url_after_uploading_to_storage("Hello World".encode(), PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        Secrets.get_application_public_key.cache_clear()
        assert self.public_key_initialization_key in TestInitialization.get_initialization_response().initialized_tasks
        assert Secrets.get_public_key_string(Secrets.get_private_key().public_key()) == Secrets.get_public_key_string(Secrets.get_application_public_key())

    def test_create_public_key_when_no_private_key(self) -> None:
        Secrets.delete_secret(APPLICATION_KEY_SECRET_NAME)
        Secrets.get_private_key.cache_clear()
        assert self.public_key_initialization_key in TestInitialization.get_initialization_response().initialized_tasks
        assert Secrets.get_public_key_string(Secrets.get_private_key().public_key()) == Secrets.get_public_key_string(Secrets.get_application_public_key())

    def test_mismatched_public_key(self) -> None:
        new_private_key: RSAPrivateKeyWithSerialization = rsa.generate_private_key(public_exponent=65537, key_size=RSA_KEY_SIZE)
        Storage.get_url_after_uploading_to_storage(new_private_key.public_key().public_bytes(Encoding.PEM, PublicFormat.PKCS1), PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        Secrets.get_application_public_key.cache_clear()
        assert self.public_key_initialization_key in TestInitialization.get_initialization_response().initialized_tasks
        assert Secrets.get_public_key_string(Secrets.get_private_key().public_key()) == Secrets.get_public_key_string()
