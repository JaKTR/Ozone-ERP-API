from typing import Dict, Any, cast, List

from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from identity_access_management import constants
from identity_access_management.exceptions import UnauthorizedRequestException
from identity_access_management.models import database
from identity_access_management.models.rest import Authorization, User

iam_app_router: APIRouter = APIRouter(prefix=constants.BASE_URL)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{constants.BASE_URL}{constants.AUTHENTICATE_URL}")


async def get_logged_in_user_data(token: str = Depends(oauth2_scheme)) -> User:
    return User(**database.User.get_user_from_authorization_token(token).get_json())


def authorize(user: User, authorized_roles: List[str] = None) -> None:
    if not database.Role.is_authorized(user.role, authorized_roles if authorized_roles is not None else []):
        raise UnauthorizedRequestException("User does not have the necessary privileges", {"authorized_roles": authorized_roles, "user_role": user.role})


@iam_app_router.post(f"{constants.AUTHENTICATE_URL}")
async def authorization(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    """
    Authorization the user; returns the JWT Authorization Token with the user's data embedded in the data
    """
    authorization_token: str = Authorization(username=form_data.username, password=form_data.password).get_authorization_token()
    authorization_token_data: Dict[str, Any] = cast(Dict[str, Any], database.User.get_data_from_authorization_token(authorization_token))
    return {"access_token": authorization_token, "token_type": "bearer", "expiry": authorization_token_data["exp"]}


@iam_app_router.post(f"{constants.USER_URL}")
async def update_user_data(updated_user: User, logged_in_user: User = Depends(get_logged_in_user_data)) -> User:
    """
    Update the user's data (including their password)
    """
    authorize(logged_in_user)
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
async def get_user_data(logged_in_user: User = Depends(get_logged_in_user_data)) -> JSONResponse:
    """
    Get the current user's data
    """
    authorize(logged_in_user)
    return database.User.get_by_username(logged_in_user.username).get_json_response()
