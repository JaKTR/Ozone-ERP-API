from typing import Dict, Any, List

import uvicorn
from fastapi import FastAPI
from starlette import status
from starlette.responses import RedirectResponse

from app.racs.authentication.models.database import Authentication
from app.racs.authentication.models.rest import AuthenticationModel

app = FastAPI()


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse("/docs", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/authenticate")
async def authenticate(authentication: AuthenticationModel) -> Authentication:
    return authentication.save().json()


@app.get("/authenticate")   #   type: ignore[no-redef]
async def authenticate() -> List[Authentication]:
    return list(Authentication.objects)


if __name__ == "__main__":
    uvicorn.run(
        "app.racs.router:app",
        host="127.0.0.1",
        port=5000,
        log_level="debug",
        reload=True,
    )
