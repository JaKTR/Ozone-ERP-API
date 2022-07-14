from typing import Dict, Any, cast, List, Optional

from fastapi import Depends, APIRouter, Form, Cookie
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import Response

from identity_access_management import constants
from identity_access_management.exceptions import UnauthorizedRequestException
from identity_access_management.models import database
from identity_access_management.models.constants import SUPER_ADMIN_ROLE
from identity_access_management.models.rest import Authorization, User, Role

iam_app_router: APIRouter = APIRouter(prefix=constants.BASE_URL)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{constants.BASE_URL}{constants.AUTHENTICATE_URL}")


async def get_logged_in_user_data(authorization_token: str = Cookie(None)) -> User:
    return User(**database.User.get_user_from_authorization_token(authorization_token).get_json())


def authorize(user: User, authorized_roles: List[str] = None) -> None:
    if not database.Role.is_authorized(user.role, authorized_roles):
        raise UnauthorizedRequestException("User does not have the necessary privileges", {"authorized_roles": authorized_roles, "user_role": user.role})


@iam_app_router.post(f"{constants.AUTHENTICATE_URL}")
async def authorization(response: Response, username: str = Form(), password: str = Form()) -> Dict[str, str]:
    """
    Authorization the user; returns the JWT Authorization Token with the user's data embedded in the data
    """
    authorization_token: str = Authorization(username=username, password=password).get_authorization_token()
    authorization_token_data: Dict[str, Any] = cast(Dict[str, Any], database.User.get_data_from_authorization_token(authorization_token))
    response.set_cookie(key="authorization_token", value=authorization_token, httponly=True, samesite="Strict")
    return {"expiry": authorization_token_data["exp"]}


@iam_app_router.patch(f"{constants.AUTHENTICATE_URL}")
async def update_user_password(authorization: Authorization, logged_in_user: User = Depends(get_logged_in_user_data)) -> None:
    """
    Updates the user's existing password
    """
    if logged_in_user.role != SUPER_ADMIN_ROLE and authorization.username != logged_in_user.username:
        raise UnauthorizedRequestException("Other users password cannot be changed", {"username_in_payload": authorization.username, "current_username": logged_in_user.username})
    authorization.save()


@iam_app_router.post(f"{constants.USER_URL}")
async def update_user_data(updated_user: User, logged_in_user: User = Depends(get_logged_in_user_data)) -> User:
    """
    Update the user's data
    """
    if updated_user.username == logged_in_user.username:
        return updated_user.save()
    else:
        raise UnauthorizedRequestException("Only user data of the current user can be updated with this endpoint", {"username_in_payload": updated_user.username, "current_username": logged_in_user.username})


@iam_app_router.put(f"{constants.USER_URL}")
async def create_new_user(new_user: User, logged_in_user: User = Depends(get_logged_in_user_data)) -> User:
    """
    Create a new user
    """
    authorize(logged_in_user)
    return new_user.save()


@iam_app_router.get(f"{constants.USER_URL}")
async def get_user_data(logged_in_user: User = Depends(get_logged_in_user_data)) -> User:
    """
    Get the current user's data
    """
    return User.get_by_username(logged_in_user.username)


@iam_app_router.get(f"{constants.ROLE_URL}")
async def get_role_data(role: str, logged_in_user: User = Depends(get_logged_in_user_data)) -> Role:
    """
    Get the role data
    """
    authorize(logged_in_user)
    return Role.get_by_role(role)


# TODO: Filter all per organization
@iam_app_router.get(f"{constants.USER_URL}{constants.USER_ALL_URL}")
async def get_all_user_data(logged_in_user: User = Depends(get_logged_in_user_data)) -> Optional[List[User]]:
    """
    Get the current user's data
    """
    authorize(logged_in_user)
    if logged_in_user.role == SUPER_ADMIN_ROLE:
        return User.get_all()
    return None
