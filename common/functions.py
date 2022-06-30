import requests


def get_data_from_url(url: str) -> bytes:
    return requests.get(url).content
