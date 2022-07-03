from functools import cache
from typing import Dict, cast

from azure.core.credentials import TokenCredential
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPrivateKey, RSAPublicKey)
from cryptography.hazmat.primitives.serialization import (Encoding,
                                                          PublicFormat)

import common.constants
import common.functions
from common import constants
from common.exceptions import (FileNotAvailableException,
                               SecretNotAvailableException)


class Secrets:
    secret_client: SecretClient = SecretClient(vault_url=constants.AZURE_KEY_VAULT_URI,
                                               credential=cast(TokenCredential, DefaultAzureCredential()))

    @classmethod
    @cache
    def get_secret(cls, secret_name: str) -> str:
        try:
            secret: str = cls.secret_client.get_secret(secret_name).value

            if secret == "":
                raise SecretNotAvailableException(secret_name)
            return secret
        except ResourceNotFoundError:
            raise SecretNotAvailableException(secret_name)

    @classmethod
    def set_secret(cls, secret_name: str, secret: str) -> None:
        try:
            cls.secret_client.set_secret(secret_name, secret)
            cls.get_secret.cache_clear()
        except ResourceExistsError:
            cls.secret_client.begin_recover_deleted_secret(secret_name).wait()
            Secrets.set_secret(secret_name, secret)

    @classmethod
    def delete_secret(cls, secret_name: str) -> None:
        try:
            cls.secret_client.begin_delete_secret(secret_name).wait()
            cls.get_secret.cache_clear()
        except ResourceNotFoundError:
            raise SecretNotAvailableException(secret_name)

    @staticmethod
    def get_application_private_key_string() -> str:
        return Secrets.get_secret(constants.APPLICATION_KEY_SECRET_NAME)

    @staticmethod
    @cache
    def get_private_key() -> RSAPrivateKey:
        return cast(RSAPrivateKey, serialization.load_pem_private_key(Secrets.get_application_private_key_string().encode(), password=None))

    @staticmethod
    @cache
    def get_application_public_key() -> RSAPublicKey:
        return cast(RSAPublicKey, serialization.load_pem_public_key(common.functions.get_data_from_url(Secrets.get_application_public_key_url())))

    @staticmethod
    def get_application_public_key_url() -> str:
        return Storage.get_url_of_file(constants.PUBLIC_KEY_FILE_NAME, constants.AZURE_STORAGE_PUBLIC_CONTAINER_NAME)

    @staticmethod
    def get_public_key_string(public_key: RSAPublicKey = None) -> str:
        if public_key is None:
            public_key = Secrets.get_application_public_key()
        return public_key.public_bytes(Encoding.PEM, PublicFormat.PKCS1).decode("UTF-8")


class Storage:
    connection_string: str = Secrets.get_secret(constants.AZURE_STORAGE_CONNECTION_STRING_SECRET_NAME)
    bob_service_client: BlobServiceClient = BlobServiceClient.from_connection_string(connection_string)

    @classmethod
    def get_url_after_uploading_to_storage(cls, data: bytes, file_name: str, container_name: str) -> str:
        container_client: ContainerClient = cls.bob_service_client.get_container_client(container_name)
        blob_client: BlobClient = container_client.upload_blob(name=file_name, data=data, overwrite=True)   # type: ignore[type-var]
        return str(blob_client.url)

    @classmethod
    def get_all_files_and_urls_from_container(cls, container_name: str) -> Dict[str, str]:
        all_files_and_urls_dict: Dict[str, str] = {}
        container_client: ContainerClient = cls.bob_service_client.get_container_client(container_name)
        for blob in container_client.list_blobs():
            all_files_and_urls_dict[blob.name] = container_client.get_blob_client(blob.name).url
        return all_files_and_urls_dict

    @classmethod
    def get_url_of_file(cls, file_name: str, container_name: str) -> str:
        all_files_and_urls_in_container: Dict[str, str] = Storage.get_all_files_and_urls_from_container(container_name)
        try:
            return all_files_and_urls_in_container[file_name]
        except KeyError:
            raise FileNotAvailableException({"file_name": file_name, "container": container_name})

    @classmethod
    def delete_file(cls, file_name: str, container_name: str) -> None:
        container_client: ContainerClient = cls.bob_service_client.get_container_client(container_name)
        for blob in container_client.list_blobs():
            if blob.name == file_name:
                container_client.get_blob_client(blob.name).delete_blob()
                return
        raise FileNotAvailableException({"file_name": file_name, "container": container_name})
