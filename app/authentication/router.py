from typing import Dict

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from app.authentication import constants
from app.authentication.exceptions import UnauthorizedRequestException
from app.authentication.models import database
from app.authentication.models.rest import Authentication, User

router = APIRouter(prefix=f"{constants.BASE_URL}")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{constants.BASE_URL}{constants.AUTHENTICATE_URL}")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return User(**database.User.get_user_from_authentication_token(token).get_json())


@router.post(f"{constants.AUTHENTICATE_URL}")
async def authenticate(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    """
    Authenticate the user; returns the JWT Authentication Token with the user's data embedded in the data
    """
    authentication: Authentication = Authentication(username=form_data.username, password=form_data.password)
    return {"access_token": authentication.get_authentication_token(), "token_type": "bearer"}


@router.post(f"{constants.SAVE_USER_URL}")
async def update_user_data(updated_user: User, user: User = Depends(get_current_user)) -> User:
    """
    Update the user's data (including their password)
    """
    if updated_user.username == user.username:
        return updated_user.save()
    else:
        raise UnauthorizedRequestException(updated_user.get_dict())


@router.put(f"{constants.SAVE_USER_URL}")
async def create_new_user(user: User) -> JSONResponse:
    """
    Create a new user
    """
    return user.save().get_json_response()


@router.get("/")
async def get_user_data(user: User = Depends(get_current_user)) -> JSONResponse:
    """
    Get the current user's data
    """
    return database.User.get_by_username(user.username).get_json_response()
