import datetime
from typing import Any, Dict

import jwt
from requests import Response
from starlette import status

import identity_access_management
from common.azure import Secrets
from identity_access_management.models import rest, database
from identity_access_management.models.constants import PBKDF2_ALGORITHM
from tests.identity_access_management import iam_test_client


def test_redirect_to_docs() -> None:
    response: Response = iam_test_client.get(f"{identity_access_management.constants.BASE_URL}")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "text/html; charset=utf-8"


class TestAuthorization:

    def test_successful(self, new_user_data: rest.User, saved_user_data: rest.User) -> None:
        response: Response = iam_test_client.post(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
            data={"username": saved_user_data.username,
                  "password": new_user_data.password})

        decoded_data: Dict[str, Any] = jwt.decode(response.json()["access_token"],
                                                  Secrets.get_application_public_key(),  # type: ignore[arg-type]
                                                  algorithms=
                                                  [identity_access_management.models.constants.PBKDF2_ALGORITHM])

        assert response.status_code == status.HTTP_200_OK
        assert database.User.get_by_username(saved_user_data.username).get_json() == decoded_data.get(
            database.User.__name__)

    def test_expired_token(self, saved_user_data: rest.User) -> None:
        user_data: database.User = database.User.get_by_username(saved_user_data.username)
        data: Dict[str, Any] = {
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(
                minutes=(identity_access_management.models.constants.AUTHORIZATION_TOKEN_EXPIRY_MINUTES + 1)),
            database.User.__name__: user_data.get_json()}
        new_authorization_token: str = str(
            jwt.encode(data, Secrets.get_private_key(),  # type: ignore[arg-type]
                       algorithm=identity_access_management.models.constants.PBKDF2_ALGORITHM))
        response: Response = iam_test_client.get(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.USER_URL}",
            headers={"Authorization": f"Bearer {new_authorization_token}"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_wrong_password(self, new_user_data: rest.User, saved_user_data: rest.User) -> None:
        new_user_data.username = saved_user_data.username
        new_user_data.password = new_user_data.password + "a"
        response: Response = iam_test_client.post(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
            data=new_user_data.get_dict())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_wrong_username(self, new_user_data: rest.User, saved_user_data: rest.User) -> None:
        new_user_data.username = saved_user_data.username + "a"
        response: Response = iam_test_client.post(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
            data=new_user_data.get_dict())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSave:

    def test_save_new_user(self, new_user_data: rest.User, super_user_request_header: Dict[str, str]) -> None:
        response: Response = iam_test_client.put(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.USER_URL}",
            json=new_user_data.get_dict(), headers=super_user_request_header)
        assert response.status_code == status.HTTP_200_OK

    def test_save_new_password(self, new_user_data: rest.User, request_header: Dict[str, str]) -> None:
        new_user_data.password = new_user_data.password = "a"
        response: Response = iam_test_client.post(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.USER_URL}",
            json=new_user_data.get_dict(),
            headers=request_header)
        assert response.status_code == status.HTTP_200_OK

    def test_save_same_password_reused(self, new_user_data: rest.User, request_header: Dict[str, str]) -> None:
        response: Response = iam_test_client.post(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.USER_URL}",
            json=new_user_data.get_dict(),
            headers=request_header)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_current_user(self, saved_user_data: rest.User, request_header: Dict[str, str]) -> None:
        response: Response = iam_test_client.get(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.USER_URL}",
            headers=request_header)
        assert response.status_code == status.HTTP_200_OK
        assert database.User.get_by_username(saved_user_data.username).get_json() == response.json()

    def test_update_different_user(self, new_user_data: rest.User, saved_user_data: rest.User,
                                   request_header: Dict[str, str]) -> None:
        new_user_data.username = saved_user_data.username + "a"
        response: Response = iam_test_client.post(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.USER_URL}",
            json=new_user_data.get_dict(), headers=request_header)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
