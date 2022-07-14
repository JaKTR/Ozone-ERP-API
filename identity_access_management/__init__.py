import azure.functions as func
import nest_asyncio
import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse

from common import router as common_router
from common.exceptions import ClientException
from identity_access_management import constants
from identity_access_management.router import iam_app_router

nest_asyncio.apply()

iam_app = FastAPI(openapi_url=f"{constants.BASE_URL}/openapi.json")
iam_app.add_middleware(
    CORSMiddleware,
    allow_origins=common_router.get_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

iam_app.include_router(iam_app_router)


@iam_app.get(constants.BASE_URL, include_in_schema=False)
async def redirect_docs() -> RedirectResponse:
    return RedirectResponse(f"{constants.BASE_URL}/")


@iam_app.get(f"{constants.BASE_URL}/", include_in_schema=False)
async def show_docs() -> HTMLResponse:
    return await common_router.show_docs()


@iam_app.exception_handler(ClientException)
async def client_exception_handler(request: Request, exception: ClientException) -> JSONResponse:
    return await common_router.client_exception_handler(request, exception)


async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Each request is redirected to the ASGI handler."""
    return func.AsgiMiddleware(iam_app).handle(req, context)  # type: ignore[no-any-return,no-untyped-call]


def run() -> None:
    uvicorn.run(
        "identity_access_management:iam_app",
        host="127.0.0.1",
        port=5000,
        log_level="debug",
        reload=True,
    )


if __name__ == "__main__":
    run()
