from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional, cast

import mongoengine
from mongoengine import Document, StringField, DateTimeField
from pymongo import MongoClient  # type: ignore[attr-defined]
from starlette.responses import JSONResponse

from app.database import constants

mongo_client: Optional[MongoClient] = None


def connect_to_database() -> None:
    global mongo_client
    if mongo_client is None:
        mongo_client = mongoengine.connect(
            host=constants.DATABASE_URI,
            db=constants.DATABASE_NAME,
            uuidRepresentation="unspecified"
        )


class DatabaseDocument(Document):  # type: ignore[misc]
    _modified_time: datetime = DateTimeField()
    _modified_user_name: str = StringField()

    meta: Dict[str, Any] = {"abstract": True}

    def save(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> "DatabaseDocument":
        self._modified_time = datetime.utcnow()
        return super().save()  # type: ignore[no-any-return]

    def is_saved(self) -> bool:
        return self._modified_time is not None

    def get_json(self, exclude_fields: List[str] = None) -> Dict[str, Any]:
        return_dict: Dict[str, Any] = self._data.copy()

        for key in return_dict.copy().keys():
            if key.startswith("_") or (exclude_fields is not None and key in exclude_fields):
                return_dict.pop(key)
            elif isinstance(return_dict[key], datetime):
                return_dict[key] = cast(datetime, return_dict[key]).isoformat()

        return return_dict

    def get_json_response(self) -> JSONResponse:
        return JSONResponse(self.get_json())


connect_to_database()
