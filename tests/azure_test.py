import requests
from cryptography.hazmat.primitives.asymmetric.rsa import (RSAPrivateKey,
                                                           RSAPublicKey)

from common.azure import Secrets, Storage
from common.constants import (AZURE_STORAGE_CONNECTION_STRING_SECRET_NAME,
                              AZURE_STORAGE_PUBLIC_CONTAINER_NAME,
                              PUBLIC_KEY_FILE_NAME)
from common.exceptions import (FileNotAvailableException,
                               SecretNotAvailableException)


class TestSecrets:
    def test_get_available_secret(self) -> None:
        assert Secrets.get_secret(AZURE_STORAGE_CONNECTION_STRING_SECRET_NAME) is not None

    def test_get_unavailable_secret(self) -> None:
        try:
            Secrets.get_secret(AZURE_STORAGE_CONNECTION_STRING_SECRET_NAME + "a")
        except SecretNotAvailableException:
            pass

    def test_set_secret(self) -> None:
        Secrets.set_secret("TEST-SECRET", "Testing")
        assert Secrets.get_secret("TEST-SECRET") == "Testing"

    def test_get_application_private_key(self) -> None:
        assert isinstance(Secrets.get_private_key(), RSAPrivateKey)

    def test_get_application_public_key(self) -> None:
        assert isinstance(Secrets.get_application_public_key(), RSAPublicKey)


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
        except FileNotAvailableException:
            pass

    def test_list_all_files_from_container(self) -> None:
        assert Storage.get_all_files_and_urls_from_container(AZURE_STORAGE_PUBLIC_CONTAINER_NAME)[
                   PUBLIC_KEY_FILE_NAME] is not None

    def test_get_url_of_uploaded_file(self) -> None:
        assert Storage.get_url_of_file(PUBLIC_KEY_FILE_NAME, AZURE_STORAGE_PUBLIC_CONTAINER_NAME) is not None

    def test_get_url_of_unavailable_file(self) -> None:
        try:
            Storage.get_url_of_file(PUBLIC_KEY_FILE_NAME + "a", AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        except FileNotAvailableException:
            pass
