import requests
from pydantic import BaseModel


class ResponseModel(BaseModel):
    pass


def get_data_from_url(url: str) -> bytes:
    return requests.get(url).content
