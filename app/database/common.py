from datetime import datetime
from typing import Dict, Any, Tuple

import mongoengine
from bson import ObjectId  # type: ignore[attr-defined]
from mongoengine import Document, StringField, DateTimeField
from pymongo import MongoClient  # type: ignore[attr-defined]

from app.database import constants

mongo_client: MongoClient = None


def connect_to_database() -> None:
    global mongo_client
    if mongo_client is None:
        mongo_client = mongoengine.connect(
            host=constants.DATABASE_URI,
            db=constants.DATABASE_NAME,
            uuidRepresentation="unspecified"
        )
    pass


class DatabaseDocument(Document):  # type: ignore[misc]
    _modified_time: datetime = DateTimeField()
    _modified_user_name: str = StringField()

    meta: Dict[str, Any] = {"abstract": True}

    def save(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> "DatabaseDocument":
        self._modified_time = datetime.utcnow()
        return super().save()  # type: ignore[no-any-return]

    def is_saved(self) -> bool:
        return self._modified_time is not None

connect_to_database()