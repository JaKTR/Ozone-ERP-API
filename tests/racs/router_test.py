from typing import Dict

import pytest
from requests import Response
from starlette import status

import racs
from tests.racs import racs_test_client


def test_redirect_to_docs() -> None:
    response: Response = racs_test_client.get(f"{racs.constants.BASE_URL}")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "text/html; charset=utf-8"


@pytest.mark.usefixtures("super_user_request_header")
def test_get_sample_roster(super_user_request_header: Dict[str, str]) -> None:
    response: Response = racs_test_client.get(f"{racs.constants.BASE_URL}{racs.constants.ROSTER_URL}",
                                              headers=super_user_request_header)
    assert response.status_code == status.HTTP_200_OK
