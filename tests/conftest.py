from typing import cast, Dict

import pytest
from requests import Response

import identity_access_management
from identity_access_management.models import rest, database
from identity_access_management.models.constants import SUPER_ADMIN_ROLE
from tests.identity_access_management import iam_test_client


@pytest.fixture(autouse=True)
def reset_data() -> None:
    database.User.drop_collection()


@pytest.fixture(autouse=True)
def super_admin_user() -> database.User:
    super_admin_user: database.User = database.User.get_by_username("john_super_user", True)

    if not super_admin_user.is_saved():
        super_admin_user.first_name = "John"
        super_admin_user.role = database.Role.get_by_role(SUPER_ADMIN_ROLE)
        super_admin_user.save_new_password("hello_world")

    return super_admin_user


@pytest.fixture
def super_user_authorization_token(super_admin_user: database.User) -> str:
    response: Response = iam_test_client.post(
        f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
        data={"username": super_admin_user.username,
              "password": "hello_world"})
    return cast(str, response.json()["access_token"])


@pytest.fixture
def super_user_request_header(super_user_authorization_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {super_user_authorization_token}"}


@pytest.fixture
def new_user_data() -> rest.User:
    return rest.User(username="john_doe", first_name="John", role=SUPER_ADMIN_ROLE, password="SomeRandomPassword")


@pytest.fixture
def saved_user_data(new_user_data: rest.User) -> rest.User:
    return new_user_data.save().copy()


@pytest.fixture
def authorization_token(saved_user_data: rest.User) -> str:
    response: Response = iam_test_client.post(
        f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
        data={"username": saved_user_data.username,
              "password": "SomeRandomPassword"})
    return cast(str, response.json()["access_token"])


@pytest.fixture
def request_header(authorization_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {authorization_token}"}
