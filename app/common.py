from typing import Any, Dict

import requests
from pydantic import BaseModel


class ResponseModel(BaseModel):

    def get_dict(self) -> Dict[str, Any]:
        return super().dict(exclude_none=True)


def get_data_from_url(url: str) -> bytes:
    return requests.get(url).content
