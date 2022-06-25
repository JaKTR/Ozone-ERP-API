from typing import Dict, Any

import jwt
import pytest
from requests import Response
from starlette import status

from app.authorization import constants
from app.authorization.models import database
from app.authorization.models.rest import Authentication
from app.azure import Secrets
from tests import test_client


@pytest.fixture(autouse=True)
def reset_data() -> None:
    database.Authentication.drop_collection()


@pytest.fixture
def new_authentication_data() -> Authentication:
    return Authentication(username="john_doe", password="this is a random password")


@pytest.fixture
def saved_authentication_data(new_authentication_data: Authentication) -> Authentication:
    new_authentication_data.save()
    return new_authentication_data


class TestSave:
    def test_save_new_user(self, new_authentication_data: Authentication) -> None:
        response: Response = test_client.post(f"{constants.BASE_URL}{constants.SAVE_URL}",
                                              json=new_authentication_data.dict())
        assert response.status_code == status.HTTP_200_OK

    def test_save_new_password(self, saved_authentication_data: Authentication) -> None:
        saved_authentication_data.password = saved_authentication_data.password + "a"
        response: Response = test_client.post(f"{constants.BASE_URL}{constants.SAVE_URL}",
                                              json=saved_authentication_data.dict())
        assert response.status_code == status.HTTP_200_OK

    def test_save_same_password_reused(self, saved_authentication_data: Authentication) -> None:
        response: Response = test_client.post(f"{constants.BASE_URL}{constants.SAVE_URL}",
                                              json=saved_authentication_data.dict())
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAuthenticate:

    def test_authenticate_successful(self, saved_authentication_data: Authentication) -> None:
        response: Response = test_client.post(f"{constants.BASE_URL}/", json=saved_authentication_data.dict())
        decoded_data: Dict[str, Any] = jwt.decode(response.json()["authentication_token"],
                                                  Secrets.get_application_public_key(),  # type: ignore[arg-type]
                                                  algorithms=["RS256"])
        assert response.status_code == status.HTTP_200_OK
        assert decoded_data == {"username": saved_authentication_data.username}

    def test_authenticate_wrong_password(self, saved_authentication_data: Authentication) -> None:
        saved_authentication_data.password = saved_authentication_data.password + "a"
        response: Response = test_client.post(f"{constants.BASE_URL}/", json=saved_authentication_data.dict())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticate_wrong_username(self, saved_authentication_data: Authentication) -> None:
        saved_authentication_data.username = saved_authentication_data.username + "a"
        response: Response = test_client.post(f"{constants.BASE_URL}/", json=saved_authentication_data.dict())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
