from requests import Response
from starlette import status

from tests import test_client


def test_redirect_to_docs() -> None:
    response: Response = test_client.get("/")
    assert response.status_code == status.HTTP_200_OK
