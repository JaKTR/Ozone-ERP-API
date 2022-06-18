from datetime import datetime
from typing import Dict, Any, Tuple

import mongoengine
from mongoengine import Document, StringField, DateTimeField
from pymongo import MongoClient  # type: ignore[attr-defined]

from app.database import constants

mongo_client: MongoClient = None


def connect_to_database() -> None:
    global mongo_client
    if mongo_client is None:
        mongo_client = mongoengine.connect(host=constants.DATABASE_URI, db=constants.DATABASE_NAME, uuidRepresentation="unspecified")
    pass


class DatabaseDocument(Document):   # type: ignore[misc]
    modified_time: datetime = DateTimeField(default=datetime.utcnow)
    modified_user_name: str = StringField()

    meta: Dict[str, Any] = {"abstract": True}

    def __repr__(self) -> str:
        return self.to_json()   # type: ignore[no-any-return]

    def save(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> "DatabaseDocument":
        connect_to_database()
        self.modified_time = datetime.utcnow()
        return super().save()   # type: ignore[no-any-return]