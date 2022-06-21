import azure.functions as func
import nest_asyncio
import uvicorn

from app import app

nest_asyncio.apply()


async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Each request is redirected to the ASGI handler."""
    return func.AsgiMiddleware(app).handle(req, context)  # type: ignore[no-any-return,no-untyped-call]


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=5000,
        log_level="debug",
        reload=True,
    )
