import os

from app import constants

DATABASE_URI: str = os.getenv("MONGO_DB_URI")
DATABASE_NAME: str = constants.APP_NAME