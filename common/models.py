from typing import Any, Dict

from pydantic import BaseModel


class ResponseModel(BaseModel):

    def get_dict(self) -> Dict[str, Any]:
        return super().dict(exclude_none=True)
