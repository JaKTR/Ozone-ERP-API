import mongoengine

from common.database import common, constants


def connect_to_mock_database() -> None:
    if common.mongo_client is not None:
        mongoengine.connection.disconnect(alias="default")

    common.mongo_client = mongoengine.connect(
        host="mongomock://localhost",
        db=constants.DATABASE_NAME,
        uuidRepresentation="unspecified"
    )


connect_to_mock_database()
