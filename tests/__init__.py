import mongoengine
from starlette.testclient import TestClient

from app import database, app
from app.database import constants
from app.database.common import mongo_client

test_client: TestClient = TestClient(app)


def setup_testing_environment() -> None:
    if database.common.mongo_client is not None:
        mongoengine.connection.disconnect(alias="default")

    database.common.mongo_client = mongoengine.connect(
        host="mongomock://localhost",
        db=constants.DATABASE_NAME,
        uuidRepresentation="unspecified"
    )


setup_testing_environment()
