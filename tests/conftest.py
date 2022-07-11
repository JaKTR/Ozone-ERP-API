from typing import cast, Dict

import pytest
from requests import Response

import identity_access_management
from identity_access_management.exceptions import UniqueDocumentNotFoundException
from identity_access_management.models import database
from identity_access_management.models.constants import SUPER_ADMIN_ROLE
from tests.identity_access_management import iam_test_client

super_admin_password: str = "hello_world"


@pytest.fixture
def super_admin_user() -> database.User:
    try:
        return database.User.get_by_username("john_super_user")
    except UniqueDocumentNotFoundException:
        return database.User(
            username="kavindu",
            first_name="Kavindu",
            last_name="Athaudha",
            email="kavindu@outlook.com",
            organization_id="2",
            mobile=2,
            role=database.Role.get_by_role(SUPER_ADMIN_ROLE)
        ).save_new_password(super_admin_password)


@pytest.fixture
def super_user_authorization_token(super_admin_user: database.User) -> str:
    response: Response = iam_test_client.post(
        f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
        data={"username": super_admin_user.username,
              "password": super_admin_password})
    return cast(str, response.json()["access_token"])


@pytest.fixture
def super_user_request_header(super_user_authorization_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {super_user_authorization_token}"}
