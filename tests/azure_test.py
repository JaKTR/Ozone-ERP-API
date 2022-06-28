import requests
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import (RSAPrivateKey,
                                                           RSAPublicKey)
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from app.azure import Secrets, Storage
from app.constants import (APPLICATION_KEY_SECRET_NAME,
                           AZURE_STORAGE_CONNECTION_STRING_SECRET_NAME,
                           AZURE_STORAGE_PUBLIC_CONTAINER_NAME,
                           PUBLIC_KEY_FILE_NAME, RSA_KEY_SIZE)
from app.exceptions import (FileNotAvailableException,
                            SecretNotAvailableException)


class TestSecrets:
    def test_get_available_secret(self) -> None:
        assert Secrets.get_secret(AZURE_STORAGE_CONNECTION_STRING_SECRET_NAME) is not None

    def test_get_unavailable_secret(self) -> None:
        try:
            Secrets.get_secret(AZURE_STORAGE_CONNECTION_STRING_SECRET_NAME + "a")
        except SecretNotAvailableException as e:
            pass

    def test_set_secret(self) -> None:
        Secrets.set_secret("TEST-SECRET", "Testing")
        assert Secrets.get_secret("TEST-SECRET") == "Testing"

    def test_create_application_private_key(self) -> None:
        assert isinstance(Secrets.create_application_private_key(), RSAPrivateKey)

    def test_get_application_private_key(self) -> None:
        assert isinstance(Secrets.get_application_private_key(), RSAPrivateKey)

    def test_get_application_public_key(self) -> None:
        assert isinstance(Secrets.get_application_public_key(), RSAPublicKey)

    def test_get_application_public_key_when_public_key_unavailable(self) -> None:
        Storage.delete_file(PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        try:
            Secrets.get_application_public_key()
        except FileNotAvailableException as e:
            pass

    def test_get_application_private_key_when_private_key_unavailable(self) -> None:
        Secrets.set_secret(APPLICATION_KEY_SECRET_NAME, "")
        assert isinstance(Secrets.get_application_private_key(), RSAPrivateKey)

    def test_get_application_private_key_when_public_key_unavailable(self) -> None:
        Storage.delete_file(PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        assert isinstance(Secrets.get_application_private_key(), RSAPrivateKey)

    def test_get_application_private_key_when_public_key_is_invalid(self) -> None:
        Storage.get_url_after_uploading_to_storage("Hello World".encode(), PUBLIC_KEY_FILE_NAME,
                                                   AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        assert Secrets.get_public_key_string(
            Secrets.get_application_private_key().public_key()) == Secrets.get_public_key_string(
            Secrets.get_application_public_key())

    def test_get_application_private_key_when_public_key_is_different(self) -> None:
        Storage.get_url_after_uploading_to_storage(rsa.generate_private_key(public_exponent=65537,
                                                                            key_size=RSA_KEY_SIZE).public_key().public_bytes(
            Encoding.PEM, PublicFormat.PKCS1), PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        assert Secrets.get_public_key_string(
            Secrets.get_application_private_key().public_key()) == Secrets.get_public_key_string(
            Secrets.get_application_public_key())


class TestStorage:
    name_of_test_file: str = "test_file.txt"

    def test_upload_file(self) -> None:
        test_data: bytes = "Hello World".encode()
        url: str = Storage.get_url_after_uploading_to_storage(test_data, self.name_of_test_file,
                                                              AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        assert requests.get(url).content == test_data

    def test_delete_file(self) -> None:
        Storage.delete_file(self.name_of_test_file, AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        assert self.name_of_test_file not in Storage.get_all_files_and_urls_from_container(
            AZURE_STORAGE_PUBLIC_CONTAINER_NAME).keys()

    def test_unavailable_delete_file(self) -> None:
        try:
            Storage.delete_file(self.name_of_test_file + "a", AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        except FileNotAvailableException as e:
            pass

    def test_list_all_files_from_container(self) -> None:
        assert Storage.get_all_files_and_urls_from_container(AZURE_STORAGE_PUBLIC_CONTAINER_NAME)[
                   PUBLIC_KEY_FILE_NAME] is not None

    def test_get_url_of_uploaded_file(self) -> None:
        assert Storage.get_url_of_file(PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME) is not None

    def test_get_url_of_unavailable_file(self) -> None:
        try:
            Storage.get_url_of_file(PUBLIC_KEY_FILE_NAME + "a", AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        except FileNotAvailableException as e:
            pass
