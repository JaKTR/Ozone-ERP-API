import pytest
from requests import Response
from starlette import status

from app.authorization import constants
from app.authorization.models import database
from app.authorization.models.rest import Authentication
from tests import test_client


@pytest.fixture(autouse=True)
def reset_data() -> None:
    database.Authentication.drop_collection()


@pytest.fixture
def new_authentication_data() -> Authentication:
    return Authentication(username="john_due", password="this is a random password")


@pytest.fixture
def saved_authentication_data(new_authentication_data: Authentication) -> Authentication:
    new_authentication_data.save()
    return new_authentication_data


def test_save_new_user(new_authentication_data: Authentication) -> None:
    response: Response = test_client.post(f"{constants.BASE_URL}{constants.SAVE_URL}",
                                          json=new_authentication_data.dict())
    assert response.status_code == status.HTTP_200_OK

def test_save_new_password(saved_authentication_data: Authentication) -> None:
    saved_authentication_data.password = saved_authentication_data.password + "a"
    response: Response = test_client.post(f"{constants.BASE_URL}{constants.SAVE_URL}",
                                          json=saved_authentication_data.dict())
    assert response.status_code == status.HTTP_200_OK


def test_save_same_password_reused(saved_authentication_data: Authentication) -> None:
    response: Response = test_client.post(f"{constants.BASE_URL}{constants.SAVE_URL}",
                                          json=saved_authentication_data.dict())
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_authenticate_successful(saved_authentication_data: Authentication) -> None:
    response: Response = test_client.post(f"{constants.BASE_URL}/", json=saved_authentication_data.dict())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["authenticated"]


def test_authenticate_wrong_password(saved_authentication_data: Authentication) -> None:
    saved_authentication_data.password = saved_authentication_data.password + "a"
    response: Response = test_client.post(f"{constants.BASE_URL}/", json=saved_authentication_data.dict())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_authenticate_wrong_username(saved_authentication_data: Authentication) -> None:
    saved_authentication_data.username = saved_authentication_data.username + "a"
    response: Response = test_client.post(f"{constants.BASE_URL}/", json=saved_authentication_data.dict())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
