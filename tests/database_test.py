from app.database import common


def test_database_connection() -> None:
    common.connect_to_database()
    assert common.mongo_client is not None
