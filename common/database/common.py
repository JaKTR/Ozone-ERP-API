from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, cast

from bson import DBRef  # type: ignore[attr-defined]
from mongoengine import DateTimeField, Document, StringField, connect
from pymongo import MongoClient  # type: ignore[attr-defined]
from starlette.responses import JSONResponse

from common.database.constants import DATABASE_URI, DATABASE_NAME

mongo_client: Optional[MongoClient] = None


def connect_to_database() -> None:
    global mongo_client
    if mongo_client is None:
        mongo_client = connect(
            host=DATABASE_URI,
            db=DATABASE_NAME,
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

    def get_json(self, exclude_fields: List[str] = None, is_full_json: bool = False) -> Dict[str, Any]:
        return_dict: Dict[str, Any] = self._data.copy()

        for key, value in return_dict.copy().items():
            if key.startswith("_") or (exclude_fields is not None and key in exclude_fields):
                return_dict.pop(key)
            elif isinstance(value, datetime):
                return_dict[key] = cast(datetime, return_dict[key]).isoformat()
            elif isinstance(value, DBRef):
                return_dict[key] = value.id
            elif isinstance(value, DatabaseDocument):
                if is_full_json:
                    return_dict[key] = value.get_json()
                else:
                    return_dict[key] = value.id

        return return_dict

    def get_json_response(self) -> JSONResponse:
        return JSONResponse(self.get_json())


connect_to_database()
