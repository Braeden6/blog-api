import hashlib
from fastapi.testclient import TestClient
from main import app
import os
import sqlite3


client = TestClient(app)

def reset_db():
    conn = sqlite3.connect("test.db")
    sql = 'DELETE FROM user'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def default_user():
    return {
        "email": "braeden.norman6gmail.com",
        "password": "test1234",
        "first_name": "Braeden",
        "last_name": "Norman",
        "phone_number": "1234567890"
    }


def test_registration():
    reset_db()


    # response = client.post("/registration", json=default_user())
    # print(response.json())
    # assert response.status_code == 200



