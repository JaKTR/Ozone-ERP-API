from typing import Dict, Any, List

from fastapi.openapi.docs import get_swagger_ui_html
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse

from common.azure import Secrets
from common.constants import ALLOWED_ORIGINS_SECRET_NAME
from common.exceptions import ClientException


async def show_docs() -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="openapi.json", title="Swagger Documentation")


async def client_exception_handler(request: Request, exception: ClientException) -> JSONResponse:
    assert request is not None
    response_content: Dict[str, Any] = {"error_message": exception.error_message}
    if exception.parameters is not None:
        response_content["parameters"] = exception.parameters

    return JSONResponse(
        status_code=exception.return_code,
        content=response_content
    )


def get_allowed_origins() -> List[Any]:
    return Secrets.get_secret(ALLOWED_ORIGINS_SECRET_NAME).split(",")
