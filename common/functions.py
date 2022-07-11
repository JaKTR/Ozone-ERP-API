import secrets
import string

import requests


def get_data_from_url(url: str) -> bytes:
    return requests.get(url).content


def get_secure_random_alphanumeric_string(length: int) -> str:
    return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
