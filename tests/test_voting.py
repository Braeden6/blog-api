import hashlib
from fastapi.testclient import TestClient
from main import app




client = TestClient(app)


def test_read_main():
    response = client.get("/login")
    assert response.status_code == 200
    assert response.json().get("salt") != None
    assert len(response.json().get("salt")) == 4

    password = str(hashlib.sha256("test1234".encode('utf-8')).hexdigest())
    response = client.post("/registration", json={"email": "braeden.norman9@gmail.com", "password": password, "first_name": "Braeden", "last_name": "Norman", "phone_number": "1234567890"})
    print(response.json())
    assert response.status_code == 200


    #response = client.

