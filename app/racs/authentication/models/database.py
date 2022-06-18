from mongoengine import StringField

from app.database.common import DatabaseDocument


class Authentication(DatabaseDocument):
    username: str = StringField()
    token: str = StringField()
