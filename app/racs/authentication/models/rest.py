from app.common import ResponseModel


class AuthenticationModel(ResponseModel):
    username: str
    token: str
