from starlette.testclient import TestClient

import super_admin

super_admin_test_client: TestClient = TestClient(super_admin.super_admin_app)