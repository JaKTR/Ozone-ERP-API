import mongoengine

from common.database import common, constants
from super_admin.models import Initialization


def connect_to_mock_database() -> None:
    if common.mongo_client is not None:
        mongoengine.connection.disconnect(alias="default")

    common.mongo_client = mongoengine.connect(
        host="mongomock://localhost",
        db=constants.DATABASE_NAME,
        uuidRepresentation="unspecified"
    )


connect_to_mock_database()
Initialization().initialize_role()
