import datetime
from typing import Any, Dict

import jwt
import pytest
from requests import Response
from starlette import status

import identity_access_management
from common.azure import Secrets
from common.exceptions import ClientException
from identity_access_management.models import rest, database
from identity_access_management.models.constants import PBKDF2_ALGORITHM
from tests.conftest import get_authorization_token_header, get_authorization_token_from_response, \
    get_authorization_cookie_from_response
from tests.identity_access_management import iam_test_client

new_user_password: str = "SomeRandomPassword"
new_user_data: rest.User = rest.User(
    username="john_doe",
    first_name="John",
    last_name="Doe",
    email="john_doe@gmail.com",
    organization_id="abcd",
    mobile=51321423,
    role=database.Role(role="test_role", name="Test Role").save().role)


@pytest.fixture
def reset_data() -> None:
    database.User.drop_collection()
    database.User.get_by_username.cache_clear()
    database.User.get_all.cache_clear()


@pytest.fixture
def saved_user_data(reset_data: None) -> rest.User:
    saved_user_data: rest.User = new_user_data.save()
    database.User.get_by_username(new_user_data.username).save_new_password(new_user_password)
    return saved_user_data


@pytest.fixture
def request_header(reset_data: None, saved_user_data: rest.User) -> Dict[str, str]:
    return get_authorization_token_header(saved_user_data.username, new_user_password)


def test_redirect_to_docs() -> None:
    response: Response = iam_test_client.get(f"{identity_access_management.constants.BASE_URL}")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "text/html; charset=utf-8"


class TestUser:

    def test_save_new_user(self, super_user_request_header: Dict[str, str]) -> None:
        response: Response = iam_test_client.put(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.USER_URL}",
            json=new_user_data.get_dict(), headers=super_user_request_header)
        assert response.status_code == status.HTTP_200_OK

    def test_get_current_user(self, saved_user_data: rest.User, request_header: Dict[str, str]) -> None:
        response: Response = iam_test_client.get(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.USER_URL}",
            headers=request_header)
        assert response.status_code == status.HTTP_200_OK
        assert database.User.get_by_username(saved_user_data.username).get_json() == response.json()

    def test_get_another_user(self, saved_user_data: rest.User, super_user_request_header: Dict[str, str]) -> None:
        response: Response = iam_test_client.get(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.USER_URL}",
            params={"username": saved_user_data.username}, headers=super_user_request_header)
        assert response.status_code == status.HTTP_200_OK
        assert database.User.get_by_username(saved_user_data.username).get_json() == response.json()

    def test_get_another_user_unauthorized(self, saved_user_data: rest.User, request_header: Dict[str, str]) -> None:
        response: Response = iam_test_client.get(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.USER_URL}",
            params={"username": saved_user_data.username + "a"}, headers=request_header)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user(self, saved_user_data: rest.User, request_header: Dict[str, str]) -> None:
        saved_user_data.last_name = saved_user_data.last_name + "a"
        response: Response = iam_test_client.post(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.USER_URL}",
            json=saved_user_data.get_dict(), headers=request_header)
        assert response.status_code == status.HTTP_200_OK
        assert database.User.get_by_username(saved_user_data.username).last_name == saved_user_data.last_name

    def test_update_different_user(self, saved_user_data: rest.User, request_header: Dict[str, str]) -> None:
        saved_user_data.username = saved_user_data.username + "a"
        response: Response = iam_test_client.post(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.USER_URL}",
            json=saved_user_data.get_dict(), headers=request_header)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_all_user_data(self, saved_user_data: rest.User, super_user_request_header: Dict[str, str]) -> None:
        another_user_data: rest.User = saved_user_data.copy()
        another_user_data.username = another_user_data.username = "a"
        another_user_data.save()

        response: Response = iam_test_client.get(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.USER_URL}{identity_access_management.constants.USER_ALL_URL}",
            json=saved_user_data.get_dict(), headers=super_user_request_header)

        assert response.status_code == status.HTTP_200_OK
        assert len(list(filter(lambda data: data["username"] == saved_user_data.username, response.json()))) == 1
        assert len(list(filter(lambda data: data["username"] == another_user_data.username, response.json()))) == 1


class TestAuthorization:

    def test_successful(self, saved_user_data: rest.User) -> None:
        response: Response = iam_test_client.post(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
            data={"username": saved_user_data.username,
                  "password": new_user_password})

        assert get_authorization_token_from_response(response) is not None
        decoded_data: Dict[str, Any] = jwt.decode(get_authorization_token_from_response(response),
                                                  Secrets.get_application_public_key(),  # type: ignore[arg-type]
                                                  algorithms=
                                                  [identity_access_management.models.constants.PBKDF2_ALGORITHM])

        assert response.status_code == status.HTTP_200_OK
        assert get_authorization_cookie_from_response(response)._rest["SameSite"] == "None"  # type: ignore[attr-defined]
        assert database.User.get_by_username(saved_user_data.username).get_json() == decoded_data.get(database.User.__name__)

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
            headers={"Cookie": f"authorization_token={new_authorization_token}"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_wrong_password(self, saved_user_data: rest.User) -> None:
        response: Response = iam_test_client.post(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
            data={"username": saved_user_data.username,
                  "password": new_user_password + "a"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_wrong_username(self, saved_user_data: rest.User) -> None:
        response: Response = iam_test_client.post(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
            data={"username": saved_user_data.username + "a",
                  "password": new_user_password})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_save_new_password(self, saved_user_data: rest.User, request_header: Dict[str, str]) -> None:
        response: Response = iam_test_client.patch(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
            json=rest.Authorization(username=saved_user_data.username, password=new_user_password + "a").get_dict(),
            headers=request_header)
        assert response.status_code == status.HTTP_200_OK

    def test_save_new_password_of_different_user(self, saved_user_data: rest.User, request_header: Dict[str, str]) -> None:
        response: Response = iam_test_client.patch(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
            json=rest.Authorization(username=saved_user_data.username + "a", password=new_user_password + "a").get_dict(),
            headers=request_header)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_save_same_password_reused(self, saved_user_data: rest.User, request_header: Dict[str, str]) -> None:
        response: Response = iam_test_client.patch(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}",
            json=rest.Authorization(username=saved_user_data.username, password=new_user_password).get_dict(),
            headers=request_header)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRole:
    @pytest.fixture
    def new_role_data(self) -> rest.Role:
        return rest.Role(role="some_random_role", name="Some random role").save()

    def test_get_role(self, super_user_request_header: Dict[str, str], new_role_data: rest.Role) -> None:
        response: Response = iam_test_client.get(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.ROLE_URL}",
            params={"role": new_role_data.role}, headers=super_user_request_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == new_role_data.get_dict()

    def test_get_unavailable_role(self, super_user_request_header: Dict[str, str], new_role_data: rest.Role) -> None:
        new_role_data.role = new_role_data.role + "a"
        response: Response = iam_test_client.get(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.ROLE_URL}",
            params={"role": new_role_data.role}, headers=super_user_request_header)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

class TestAppliance:

    @pytest.fixture
    def new_appliance_data(self, super_user_request_header: Dict[str, str]) -> rest.Appliance:
        return self.test_save_appliance(super_user_request_header)

    def test_save_appliance(self, super_user_request_header: Dict[str, str]) -> rest.Appliance:
        new_appliance_data: rest.Appliance = rest.Appliance(
            callsign=123,
            seats=["Seat 1", "Seat 2"],
            type="Type 1",
            is_rostered=False,
            is_checked=True,
            is_self_rostered=False
        )

        response: Response = iam_test_client.put(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.APPLIANCE_URL}",
            json=new_appliance_data.get_dict(), headers=super_user_request_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == new_appliance_data.get_dict()
        return new_appliance_data

    def test_get_appliance(self, super_user_request_header: Dict[str, str], new_appliance_data: rest.Appliance) -> None:
        response: Response = iam_test_client.get(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.APPLIANCE_URL}",
            params={"callsign": new_appliance_data.callsign}, headers=super_user_request_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == new_appliance_data.get_dict()

    def test_delete_appliance(self, super_user_request_header: Dict[str, str], new_appliance_data: rest.Appliance) -> None:
        response: Response = iam_test_client.delete(
            f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.APPLIANCE_URL}",
            params={"callsign": new_appliance_data.callsign}, headers=super_user_request_header)
        assert response.status_code == status.HTTP_200_OK
        with pytest.raises(ClientException):
            rest.Appliance.get_by_callsign(new_appliance_data.callsign)