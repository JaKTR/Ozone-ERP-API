import azure.functions as func
import nest_asyncio
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse

from common import router as common_router
from common.exceptions import ClientException
from super_admin import constants
from super_admin.router import super_admin_router

nest_asyncio.apply()

super_admin_app = FastAPI(openapi_url=f"{constants.BASE_URL}/openapi.json")
super_admin_app.add_middleware(
    CORSMiddleware,
    allow_origins=common_router.get_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

super_admin_app.include_router(super_admin_router)


@super_admin_app.get(constants.BASE_URL, include_in_schema=False)
async def redirect_docs() -> RedirectResponse:
    return RedirectResponse(f"{constants.BASE_URL}/")


@super_admin_app.get(f"{constants.BASE_URL}/", include_in_schema=False)
async def show_docs() -> HTMLResponse:
    return await common_router.show_docs()


@super_admin_app.exception_handler(ClientException)
async def client_exception_handler(request: Request, exception: ClientException) -> JSONResponse:
    return await common_router.client_exception_handler(request, exception)


async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Each request is redirected to the ASGI handler."""
    return func.AsgiMiddleware(super_admin_app).handle(req, context)  # type: ignore[no-any-return,no-untyped-call]


def run() -> None:
    uvicorn.run(
        "super_admin:super_admin_app",
        host="127.0.0.1",
        port=5000,
        log_level="debug",
        reload=True,
    )


if __name__ == "__main__":
    run()
