from typing import Dict

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from app.authentication import constants
from app.authentication.models import database
from app.authentication.models.rest import Authentication
from app.authentication.models.rest import User

router = APIRouter(prefix=f"{constants.BASE_URL}")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{constants.BASE_URL}{constants.AUTHENTICATE_URL}")


async def get_current_user(authentication_token: str = Depends(oauth2_scheme)) -> User:
    return User(**database.User.get_user_from_authentication_token(authentication_token).get_json())


@router.post(f"{constants.AUTHENTICATE_URL}")
async def authenticate(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    authentication: Authentication = Authentication(username=form_data.username, password=form_data.password)
    return {"authentication_token": authentication.get_authentication_token(), "token_type": "bearer"}


@router.post(f"{constants.SAVE_USER_URL}")
async def update(authentication: Authentication, authorization_token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    authentication.save()
    return {"status": "OK"}


@router.put(f"{constants.SAVE_USER_URL}")
async def create(user: User) -> JSONResponse:
    return user.save().get_json_response()


@router.get(f"/")
async def get(user: User = Depends(get_current_user)) -> JSONResponse:
    return database.User.get_by_username(user.username).get_json_response()
