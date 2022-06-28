import datetime
from typing import Any, Dict, cast

import jwt
import pytest
from requests import Response
from starlette import status

import app.authentication.models.constants
from app.authentication import constants
from app.authentication.models import database, rest
from app.azure import Secrets
from tests import test_client


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
def authentication_token(new_user_data: rest.User, saved_user_data: rest.User) -> str:
    response: Response = test_client.post(f"{constants.BASE_URL}{constants.AUTHENTICATE_URL}",
                                          data={"username": saved_user_data.username,
                                                "password": new_user_data.password})
    return cast(str, response.json()["access_token"])


@pytest.fixture
def request_header(authentication_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {authentication_token}"}


class TestAuthenticate:
    def test_successful(self, new_user_data: rest.User, saved_user_data: rest.User) -> None:
        response: Response = test_client.post(f"{constants.BASE_URL}{constants.AUTHENTICATE_URL}",
                                              data={"username": saved_user_data.username,
                                                    "password": new_user_data.password})

        decoded_data: Dict[str, Any] = jwt.decode(response.json()["access_token"],
                                                  Secrets.get_application_public_key(),  # type: ignore[arg-type]
                                                  algorithms=[app.authentication.models.constants.PBKDF2_ALGORITHM])

        assert response.status_code == status.HTTP_200_OK
        assert database.User.get_by_username(saved_user_data.username).get_json() == decoded_data.get(
            database.User.__name__)

    def test_expired_token(self, saved_user_data: rest.User) -> None:
        user_data: database.User = database.User.get_by_username(saved_user_data.username)
        data: Dict[str, Any] = {
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(
                minutes=(app.authentication.models.constants.AUTHORIZATION_TOKEN_EXPIRY_MINUTES + 1)),
            database.User.__name__: user_data.get_json()}
        new_authentication_token: str = str(jwt.encode(data, Secrets.get_application_private_key(), # type: ignore[arg-type]
                                                       algorithm=app.authentication.models.constants.PBKDF2_ALGORITHM))
        response: Response = test_client.get(f"{constants.BASE_URL}",
                                             headers={"Authorization": f"Bearer {new_authentication_token}"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_wrong_password(self, new_user_data: rest.User, saved_user_data: rest.User) -> None:
        new_user_data.username = saved_user_data.username
        new_user_data.password = new_user_data.password + "a"
        response: Response = test_client.post(f"{constants.BASE_URL}{constants.AUTHENTICATE_URL}",
                                              data=new_user_data.get_dict())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_wrong_username(self, new_user_data: rest.User, saved_user_data: rest.User) -> None:
        new_user_data.username = saved_user_data.username + "a"
        response: Response = test_client.post(f"{constants.BASE_URL}{constants.AUTHENTICATE_URL}",
                                              data=new_user_data.get_dict())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSave:
    def test_save_new_user(self, new_user_data: rest.User) -> None:
        response: Response = test_client.put(f"{constants.BASE_URL}{constants.SAVE_USER_URL}",
                                             json=new_user_data.get_dict())
        assert response.status_code == status.HTTP_200_OK

    def test_save_new_password(self, new_user_data: rest.User, request_header: Dict[str, str]) -> None:
        new_user_data.password = new_user_data.password = "a"
        response: Response = test_client.post(f"{constants.BASE_URL}{constants.SAVE_USER_URL}",
                                              json=new_user_data.get_dict(),
                                              headers=request_header)
        assert response.status_code == status.HTTP_200_OK

    def test_save_same_password_reused(self, new_user_data: rest.User, request_header: Dict[str, str]) -> None:
        response: Response = test_client.post(f"{constants.BASE_URL}{constants.SAVE_USER_URL}",
                                              json=new_user_data.get_dict(),
                                              headers=request_header)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_current_user(self, saved_user_data: rest.User, request_header: Dict[str, str]) -> None:
        response: Response = test_client.get(f"{constants.BASE_URL}",
                                             headers=request_header)
        assert response.status_code == status.HTTP_200_OK
        assert database.User.get_by_username(saved_user_data.username).get_json() == response.json()

    def test_update_different_user(self, new_user_data: rest.User, saved_user_data: rest.User, request_header: Dict[str, str]) -> None:
        new_user_data.username = saved_user_data.username + "a"
        response: Response = test_client.post(f"{constants.BASE_URL}{constants.SAVE_USER_URL}",
                                             json=new_user_data.get_dict(), headers=request_header)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
