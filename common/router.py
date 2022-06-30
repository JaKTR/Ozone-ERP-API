from typing import Dict, Any

from fastapi import Request
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import JSONResponse, HTMLResponse

from common.exceptions import ClientException


async def show_docs() -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="openapi.json", title="Swagger Documentation")


async def client_exception_handler(request: Request, exception: ClientException) -> JSONResponse:
    response_content: Dict[str, Any] = {"error_message": exception.error_message}
    if exception.parameters is not None:
        response_content["parameters"] = exception.parameters

    return JSONResponse(
        status_code=exception.return_code,
        content=response_content
    )
