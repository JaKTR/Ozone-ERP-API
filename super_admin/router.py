from fastapi import APIRouter

from super_admin import constants
from super_admin.models import Initialization

super_admin_router: APIRouter = APIRouter(prefix=constants.BASE_URL)


@super_admin_router.post(f"{constants.INITIALIZE_URL}")
async def initialize() -> Initialization:
    """
    Initialize the application for first start up
    """
    return Initialization.initialize()
