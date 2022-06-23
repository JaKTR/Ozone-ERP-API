import typing
from functools import cache
from typing import Dict

from azure.core.credentials import TokenCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey, RSAPrivateKeyWithSerialization
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.serialization import PublicFormat

from app import constants, common
from app.exceptions import SecretNotAvailableException, FileNotAvailableException


class Secrets:
    secret_client: SecretClient = SecretClient(vault_url=constants.AZURE_KEY_VAULT_URI, credential=typing.cast(TokenCredential, DefaultAzureCredential()))

    @classmethod
    @cache
    def get_secret(cls, secret_name: str) -> str:
        try:
            return cls.secret_client.get_secret(secret_name).value
        except ResourceNotFoundError as e:
            raise SecretNotAvailableException(secret_name)

    @classmethod
    def set_secret(cls, secret_name: str, secret: str) -> None:
        cls.secret_client.set_secret(secret_name, secret)

    @staticmethod
    def create_application_private_key() -> RSAPrivateKey:
        private_key: RSAPrivateKeyWithSerialization = rsa.generate_private_key(public_exponent=65537, key_size=constants.RSA_KEY_SIZE)
        Secrets.set_secret(constants.APPLICATION_KEY_SECRET_NAME, private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode("UTF-8"))
        Storage.get_url_after_uploading_to_storage(private_key.public_key().public_bytes(Encoding.PEM, PublicFormat.PKCS1), constants.PUBLIC_KEY_FILE_NAME, constants.AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        return private_key

    @staticmethod
    def get_application_private_key() -> RSAPrivateKey:
        try:

            key_string: str = Secrets.get_secret(constants.APPLICATION_KEY_SECRET_NAME)
            private_key: RSAPrivateKey = serialization.load_pem_private_key(key_string.encode(), password=None)

            if Secrets.get_public_key_string(private_key.public_key()) != Secrets.get_public_key_string(Secrets.get_application_public_key()):
                return Secrets.create_application_private_key()
            return private_key

        except SecretNotAvailableException as e:
            return Secrets.create_application_private_key()

    @staticmethod
    def get_application_public_key() -> RSAPublicKey:
        return typing.cast(RSAPublicKey, serialization.load_pem_public_key(common.get_data_from_url(Secrets.get_application_public_key_url())))

    @staticmethod
    def get_application_public_key_url() -> str:
        try:
            return Storage.get_url_of_file(constants.PUBLIC_KEY_FILE_NAME, constants.AZURE_STORAGE_PUBLIC_CONTAINER_NAME)
        except FileNotAvailableException as e:
            Secrets.create_application_private_key()
            return Storage.get_url_of_file(constants.PUBLIC_KEY_FILE_NAME, constants.AZURE_STORAGE_PUBLIC_CONTAINER_NAME)

    @staticmethod
    def get_public_key_string(public_key: RSAPublicKey) -> str:
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
        if file_name in all_files_and_urls_in_container:
            return all_files_and_urls_in_container[file_name]
        else:
            raise FileNotAvailableException({"file_name": file_name, "container": container_name})

    @classmethod
    def delete_file(cls, file_name: str, container_name: str) -> None:
        container_client: ContainerClient = cls.bob_service_client.get_container_client(container_name)
        for blob in container_client.list_blobs():
            if blob.name == file_name:
                container_client.get_blob_client(blob.name).delete_blob()
                return
