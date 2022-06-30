from starlette.testclient import TestClient

import racs

racs_test_client: TestClient = TestClient(racs.racs_app)
