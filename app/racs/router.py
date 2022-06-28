from fastapi import APIRouter

from app.racs import constants

router = APIRouter(prefix=f"/{constants.BASE_URL}")
