import pytest
from api_client import ApiClient


@pytest.fixture(scope="session")
def api():
    return ApiClient()


@pytest.fixture(scope="session")
def ref_data(api):
    return {
        "priorities": api.get_priorities(),
        "types": api.get_types(),
        "statuses": api.get_statuses(),
        "departments": api.get_departments(),
        "staff_users": api.get_staff_users()
    }