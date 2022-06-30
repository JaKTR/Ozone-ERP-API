from typing import Dict

from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from identity_access_management import constants
from identity_access_management.exceptions import UnauthorizedRequestException
from identity_access_management.models import database
from identity_access_management.models.rest import Authorization, User

iam_app_router: APIRouter = APIRouter(prefix=constants.BASE_URL)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{constants.BASE_URL}{constants.AUTHENTICATE_URL}")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return User(**database.User.get_user_from_authorization_token(token).get_json())


@iam_app_router.post(f"{constants.AUTHENTICATE_URL}")
async def authorization(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    """
    Authorization the user; returns the JWT Authorization Token with the user's data embedded in the data
    """
    authorization: Authorization = Authorization(username=form_data.username, password=form_data.password)
    return {"access_token": authorization.get_authorization_token(), "token_type": "bearer"}


@iam_app_router.post(f"{constants.USER_URL}")
async def update_user_data(updated_user: User, user: User = Depends(get_current_user)) -> User:
    """
    Update the user's data (including their password)
    """
    if updated_user.username == user.username:
        return updated_user.save()
    else:
        raise UnauthorizedRequestException(updated_user.get_dict())


@iam_app_router.put(f"{constants.USER_URL}")
async def create_new_user(user: User) -> JSONResponse:
    """
    Create a new user
    """
    return user.save().get_json_response()


@iam_app_router.get(f"{constants.USER_URL}")
async def get_user_data(user: User = Depends(get_current_user)) -> JSONResponse:
    """
    Get the current user's data
    """
    return database.User.get_by_username(user.username).get_json_response()
