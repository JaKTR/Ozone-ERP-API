import azure.functions as func
import nest_asyncio

nest_asyncio.apply()

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
  """Each request is redirected to the ASGI handler.
    """
  return func.AsgiMiddleware(app.racs.router.app).handle(req, context)  # type: ignore