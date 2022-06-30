from common import constants
from common.azure import Secrets

MONGO_DB_URI_SECRET_NAME: str = "MONGO-DB-URI"
DATABASE_URI: str = Secrets.get_secret(MONGO_DB_URI_SECRET_NAME)
DATABASE_NAME: str = constants.APP_NAME
