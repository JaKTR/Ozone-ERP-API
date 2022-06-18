from datetime import datetime
from typing import Dict, Any, Tuple

import mongoengine
from mongoengine import Document, StringField, DateTimeField
from pymongo import MongoClient

from app.database import constants

mongo_client: MongoClient = None


def connect_to_database() -> None:
    global mongo_client
    if mongo_client is None:
        mongo_client = mongoengine.connect(host=constants.DATABASE_URI, dbmy=constants.DATABASE_NAME)
    pass


class DatabaseDocument(Document):
    modified_time: datetime = DateTimeField(default=datetime.utcnow)
    modified_user_name: str = StringField()

    meta: Dict[str, Any] = {"abstract": True}

    def __repr__(self) -> str:
        return self.to_json()

    def save(self, *args: Tuple, **kwargs: Dict[str, Any]) -> "DatabaseDocument":
        connect_to_database()
        self.modified_time = datetime.utcnow()
        return super().save()