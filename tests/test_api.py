from typing import *
from fastapi.testclient import TestClient
from urllib.parse import urlencode
from server import app
from server.api import GoodbyePayload

client = TestClient(app)

def make_url(baseurl, to_send:Dict[str, Any]):
    return baseurl + "?" + urlencode(to_send)

def test_hello():
    response = client.get(make_url("/api/get-a-hi", {"firstname": "bob"}))
    assert response.status_code == 200
    assert response.json() == "Hello bob"

def test_goodbye():
    request = {"firstname": "bob"}
    response = client.post("/api/post-a-bye", json=request)
    assert response.status_code == 200
    assert response.json() == "Goodbye bob"

def test_empty_goodbye():
    request = {"firstname": ""}
    response = client.post("/api/post-a-bye", json=request)
    assert response.status_code == 200
    assert response.json() == "Goodbye "