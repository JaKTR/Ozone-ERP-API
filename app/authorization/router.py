from typing import Dict

from fastapi import APIRouter

from app.authorization import constants
from app.authorization.models.rest import Authentication

router = APIRouter(prefix=f"{constants.BASE_URL}")


@router.post("/")
async def authenticate(authentication: Authentication) -> Dict[str, bool]:
    return {"authenticated": authentication.authorize()}


@router.post(f"{constants.SAVE_URL}")
async def save(authentication: Authentication) -> Dict[str, str]:
    authentication.save()
    return {"status": "OK"}
