from typing import Dict, Any

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from app.authorization.router import router as authorization_router
from app.exceptions import ClientException
from app.racs.router import router as racs_router
from app.router import router as main_router

app = FastAPI()
app.include_router(main_router)
app.include_router(racs_router)
app.include_router(authorization_router)


@app.exception_handler(ClientException)
async def client_exception_handler(request: Request, exception: ClientException) -> JSONResponse:
    response_content: Dict[str, Any] = {"error_message": exception.error_message}
    if exception.parameters is not None:
        response_content["parameters"] = exception.parameters

    return JSONResponse(
        status_code=exception.return_code,
        content=response_content
    )
