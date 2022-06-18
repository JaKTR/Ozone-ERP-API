import logging

import azure.functions as func
import nest_asyncio

from app.database import constants
from app.racs.router import app

nest_asyncio.apply()

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
  """Each request is redirected to the ASGI handler.
    """
  logging.info("Database URI:")
  logging.info(constants.DATABASE_URI)
  logging.info("End")
  return func.AsgiMiddleware(app).handle(req, context)  # type: ignore[no-any-return,no-untyped-call]