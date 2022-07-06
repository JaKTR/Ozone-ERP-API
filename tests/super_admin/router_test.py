from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPrivateKeyWithSerialization
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from requests import Response

from common.azure import Secrets, Storage
from common.constants import APPLICATION_KEY_SECRET_NAME, PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME, RSA_KEY_SIZE
from identity_access_management.models import database
from super_admin import constants
from super_admin.models import Initialization
from tests.super_admin import super_admin_test_client


def get_initialization_response() -> Initialization:
    response: Response = super_admin_test_client.post(f"{constants.BASE_URL}{constants.INITIALIZE_URL}")
    return Initialization(**response.json())


def test_create_super_admin_role() -> None:
    database.Role.drop_collection()
    assert "Role" in get_initialization_response().initialized_tasks


def test_no_private_key() -> None:
    Secrets.delete_secret(APPLICATION_KEY_SECRET_NAME)
    Secrets.get_private_key.cache_clear()
    assert "Private Key" in get_initialization_response().initialized_tasks
    assert isinstance(Secrets.get_private_key(), RSAPrivateKey)


def test_invalid_private_key() -> None:
    Secrets.set_secret(APPLICATION_KEY_SECRET_NAME, "")
    Secrets.get_private_key.cache_clear()
    assert "Private Key" in get_initialization_response().initialized_tasks
    assert isinstance(Secrets.get_private_key(), RSAPrivateKey)


def test_no_public_key() -> None:
    Storage.delete_file(PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
    Secrets.get_application_public_key.cache_clear()
    assert "Public Key" in get_initialization_response().initialized_tasks
    assert Secrets.get_public_key_string(Secrets.get_private_key().public_key()) == Secrets.get_public_key_string(Secrets.get_application_public_key())


def test_invalid_public_key() -> None:
    Storage.get_url_after_uploading_to_storage("Hello World".encode(), PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
    Secrets.get_application_public_key.cache_clear()
    assert "Public Key" in get_initialization_response().initialized_tasks
    assert Secrets.get_public_key_string(Secrets.get_private_key().public_key()) == Secrets.get_public_key_string(Secrets.get_application_public_key())


def test_mismatched_public_key() -> None:
    new_private_key: RSAPrivateKeyWithSerialization = rsa.generate_private_key(public_exponent=65537, key_size=RSA_KEY_SIZE)
    Storage.get_url_after_uploading_to_storage(new_private_key.public_key().public_bytes(Encoding.PEM, PublicFormat.PKCS1), PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
    Secrets.get_application_public_key.cache_clear()
    assert "Public Key" in get_initialization_response().initialized_tasks
    assert Secrets.get_public_key_string(Secrets.get_private_key().public_key()) == Secrets.get_public_key_string()
