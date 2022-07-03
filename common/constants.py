import os

APP_NAME: str = "Umbrella"
ENVIRONMENT: str = "Development"

AZURE_KEY_VAULT_NAME: str = os.getenv("KEY_VAULT_NAME")
AZURE_KEY_VAULT_URI: str = f"https://{AZURE_KEY_VAULT_NAME}.vault.azure.net"
APPLICATION_KEY_SECRET_NAME: str = f"{APP_NAME}-RSA-Key"

AZURE_STORAGE_CONNECTION_STRING_SECRET_NAME: str = "AZURE-STORAGE-CONNECTION-STRING"
AZURE_STORAGE_PUBLIC_CONTAINER_NAME: str = f"{APP_NAME.lower()}-erp-api-{ENVIRONMENT.lower()}-public"
PUBLIC_KEY_FILE_NAME: str = f"{APP_NAME.lower()}-public-key-{ENVIRONMENT.lower()}.pub"
RSA_KEY_SIZE: int = 4096
