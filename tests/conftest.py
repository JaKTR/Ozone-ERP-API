from http.cookiejar import Cookie
from typing import Dict

import pytest
from requests import Response

import identity_access_management
from identity_access_management.exceptions import UniqueDocumentNotFoundException
from identity_access_management.models import database
from identity_access_management.models.constants import SUPER_ADMIN_ROLE
from tests.identity_access_management import iam_test_client


def get_authorization_cookie_from_response(response: Response) -> Cookie:
    return next(filter(lambda cookie: cookie.name == 'authorization_token', response.cookies))


def get_authorization_token_from_response(response: Response) -> str:
    return get_authorization_cookie_from_response(response).value


def get_authorization_token_header(username: str, password: str) -> Dict[str, str]:
    response: Response = iam_test_client.post(
        f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
        data={"username": username,
              "password": password})
    return {"Cookie": f"authorization_token={get_authorization_token_from_response(response)}"}


@pytest.fixture
def super_user_request_header() -> Dict[str, str]:
    super_admin_user: database.User
    super_admin_password: str = "hello_world"
    try:
        super_admin_user = database.User.get_by_username("john_super_user")
    except UniqueDocumentNotFoundException:
        super_admin_user = database.User(
            username="kavindu",
            first_name="Kavindu",
            last_name="Athaudha",
            email="kavindu@outlook.com",
            organization_id="2",
            mobile=2,
            role=database.Role.get_by_role(SUPER_ADMIN_ROLE)
        ).save_new_password(super_admin_password)

    return get_authorization_token_header(super_admin_user.username, super_admin_password)
