from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import JSONResponse

import identity_access_management
from identity_access_management.models import database
from identity_access_management.models.rest import User
from racs import constants

racs_app_router: APIRouter = APIRouter(prefix=constants.BASE_URL)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return User(**database.User.get_user_from_authorization_token(token).get_json())


@racs_app_router.get(f"{constants.ROSTER_URL}")
async def get_roster_data(user: User = Depends(get_current_user)) -> JSONResponse:
    """
    Get the current user's data
    """
    return JSONResponse({"Logged in username": user.username, "Roster data": "Sample roster data here"})
