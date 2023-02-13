from fastapi.testclient import TestClient
from main import app
import sqlite3
import json


client = TestClient(app)

def reset_users():
    conn = sqlite3.connect("test.db")
    sql = 'DELETE FROM user'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def default_user():
    return {
        "email": "braeden.norman6@gmail.com",
        "password": "test1234",
        "first_name": "Braeden",
        "last_name": "Norman",
        "phone_number": "1234567890"
    }

def setup_duplicate():
    reset_users()
    response = client.post("/registration", json=default_user())
    assert response.status_code == 200


def test_duplicate_basic():
    setup_duplicate()
    response = client.post("/registration", json=default_user())
    assert response.status_code == 400
    assert response.content == b'{"detail":"User already exists with that email"}'

def test_duplicate_phone():
    setup_duplicate()
    new_user = default_user()
    new_user["phone"] = "2234567890"
    response = client.post("/registration", json=new_user)
    assert response.status_code == 400
    assert response.content == b'{"detail":"User already exists with that email"}'

def test_duplicate_email():
    setup_duplicate()
    new_user = default_user()
    new_user["email"] = "braeden.norman7@gmail.com"
    response = client.post("/registration", json=new_user)
    assert response.status_code == 400
    assert response.content == b'{"detail":"User already exists with that phone number"}'

def test_invalid_email():
    reset_users()
    new_user = default_user()
    new_user["email"] = "braeden.norman7gmail.com"
    response = client.post("/registration", json=new_user)
    assert response.status_code == 400
    assert response.content == b'{"detail":"Invalid email"}'

    new_user["email"] = "@gmail.com"
    response = client.post("/registration", json=new_user)
    assert response.status_code == 400
    assert response.content == b'{"detail":"Invalid email"}'

    new_user["email"] = "braeden.norman7@gmail"
    response = client.post("/registration", json=new_user)
    assert response.status_code == 400
    assert response.content == b'{"detail":"Invalid email"}'

def test_name_too_short():
    reset_users()
    new_user = default_user()
    new_user["first_name"] = "B"
    response = client.post("/registration", json=new_user)
    assert response.status_code == 400
    assert response.content == b'{"detail":"Name must be at least 2 characters long"}'

    new_user["first_name"] = "Braeden"
    new_user["last_name"] = "N"
    response = client.post("/registration", json=new_user)
    assert response.status_code == 400
    assert response.content == b'{"detail":"Name must be at least 2 characters long"}'

def test_password_too_short():
    reset_users()
    new_user = default_user()
    new_user["password"] = "test123"
    response = client.post("/registration", json=new_user)
    assert response.status_code == 400
    assert response.content == b'{"detail":"Password must be at least 8 characters long"}'

def test_login_basic():
    reset_users()
    new_user = default_user()
    response = client.post("/registration", json=default_user())
    assert response.status_code == 200

    response = client.post("/login", 
        data={
            "username": new_user["email"],
            "password": new_user["password"]
        }, 
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    results = response.json()
    assert results["token"] != None
    assert results["email"] == new_user["email"]
    assert results["first_name"] == new_user["first_name"]
    assert results["last_name"] == new_user["last_name"]
    assert results["id"] == 1
    assert results["role"] == 'user'







