from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import JSONResponse

import identity_access_management
from identity_access_management.models.rest import User
from identity_access_management.router import get_logged_in_user_data
from racs import constants

racs_app_router: APIRouter = APIRouter(prefix=constants.BASE_URL)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{identity_access_management.constants.BASE_URL}{identity_access_management.constants.AUTHENTICATE_URL}")


@racs_app_router.get(f"{constants.ROSTER_URL}")
async def get_roster_data(user: User = Depends(get_logged_in_user_data)) -> JSONResponse:
    """
    Get the current user's data
    """
    return JSONResponse({"Logged in username": user.username, "Roster data": "Sample roster data here"})
