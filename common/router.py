from typing import Dict, Any

from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import JSONResponse, HTMLResponse

from common.exceptions import ClientException
from identity_access_management.models import constants
from identity_access_management.models.database import Role


async def show_docs() -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="openapi.json", title="Swagger Documentation")


async def client_exception_handler(exception: ClientException) -> JSONResponse:
    response_content: Dict[str, Any] = {"error_message": exception.error_message}
    if exception.parameters is not None:
        response_content["parameters"] = exception.parameters

    return JSONResponse(
        status_code=exception.return_code,
        content=response_content
    )


async def initialize_data() -> None:
    Role(role_id=constants.SUPER_ADMIN_ROLE).save()
