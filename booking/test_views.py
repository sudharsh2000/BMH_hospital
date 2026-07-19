from rest_framework.test import APIClient
import pytest
@pytest.mark.django_db
def test_get_doctors():
    client=APIClient()
    response=client.get('/booking/api/doctor/')
    assert response.status_code == 200