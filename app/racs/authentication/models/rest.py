from app.common import ResponseModel
from app.racs.authentication.models import database


class AuthenticationModel(ResponseModel):
    username: str
    token: str

    def save(self) -> database.Authentication:
        return database.Authentication(**self.dict()).save()