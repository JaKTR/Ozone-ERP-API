from starlette.testclient import TestClient

import identity_access_management

iam_test_client: TestClient = TestClient(identity_access_management.iam_app)
