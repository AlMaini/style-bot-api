import requests


def test_api_endpoint():
    url = "http://localhost:8000/api/endpoint"
    response = requests.get(url)
    assert response.status_code == 200
