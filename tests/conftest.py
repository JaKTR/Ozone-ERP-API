from typing import cast, Dict

import pytest
from requests import Response

import identity_access_management
from identity_access_management.models import rest, database
from tests.identity_access_management import iam_test_client


@pytest.fixture(autouse=True)
def reset_data() -> None:
    database.User.drop_collection()


@pytest.fixture
def new_user_data() -> rest.User:
    return rest.User(username="john_doe", first_name="John", password="SomeRandomPassword")


@pytest.fixture
def saved_user_data(new_user_data: rest.User) -> rest.User:
    return new_user_data.save()


@pytest.fixture
def authorization_token(new_user_data: rest.User, saved_user_data: rest.User) -> str:
    response: Response = iam_test_client.post(
        f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
        data={"username": saved_user_data.username,
              "password": new_user_data.password})
    return cast(str, response.json()["access_token"])


@pytest.fixture
def request_header(authorization_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {authorization_token}"}
