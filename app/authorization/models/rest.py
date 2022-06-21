from app.authorization.exceptions import UsernameNotFoundException, UnauthorizedLoginException
from app.authorization.models import database
from app.common import ResponseModel


class Authentication(ResponseModel):
    username: str
    password: str

    def save(self) -> None:
        try:
            database.Authentication.get_by_username(self.username).save_new_password(self.password)
        except UsernameNotFoundException as e:
            database.Authentication(self.username).save_new_password(self.password)

    def authorize(self) -> bool:
        unauthorized_exception: UnauthorizedLoginException = UnauthorizedLoginException(
            "Incorrect username and password combination", {"username": self.username})
        try:
            if not database.Authentication.get_by_username(self.username).is_password_correct(self.password):
                raise unauthorized_exception
        except UsernameNotFoundException as e:
            raise unauthorized_exception

        # TODO: Implement JWT Token
        return True
