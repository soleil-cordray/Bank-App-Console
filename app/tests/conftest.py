# tests/conftest.py
# pytest runs this automatically before the tests.
# It swaps the real MongoDB for mongomock (a fake MongoDB that lives in memory),
# so the tests work on any laptop without installing or starting MongoDB.

import os

import mongomock
import pymongo
import pytest

# Fixed admin login for the tests (set before app/auth.py reads it, so .env can't change it)
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "admin123"

# Must happen BEFORE app.database is imported, because it connects as soon as it's imported
pymongo.MongoClient = mongomock.MongoClient

from fastapi.testclient import TestClient

from app import database
from app.main import app

ADMIN = ("admin", "admin123")
PASSWORD = "password123"


@pytest.fixture
def client():
    # Every test starts with empty collections, so IDs start at 1 again
    for name in database.db.list_collection_names():
        database.db[name].delete_many({})
    # `with` runs the app's startup (ping + create_indexes), like the real server
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def bank(client):
    '''A small bank used by most tests:
         branch 1 (DT01)
         customer 1 rohit: 0000000001 CHECKING 500, 0000000002 SAVINGS 200
         customer 2 mohit: 0000000003 CHECKING 100
    '''
    assert client.post("/api/v1/branches", json={"branch_code": "DT01", "location": "1 Main St"}, auth=ADMIN).status_code == 201
    for username in ("rohit", "mohit"):
        response = client.post("/api/v1/customers", json=customer_body(username))
        assert response.status_code == 201, response.text
    open_account(client, "rohit", 1, "CHECKING", 500)
    open_account(client, "rohit", 1, "SAVINGS", 200)
    open_account(client, "mohit", 2, "CHECKING", 100)
    return client


def customer_body(username, branch_id=1, password=PASSWORD):
    return {
        "name": username.title(),
        "email": f"{username}@example.com",
        "branch_id": branch_id,
        "username": username,
        "password": password,
    }


def login(username):
    # the `auth=` value for a customer's requests
    return (username, PASSWORD)


def open_account(client, username, owner_id, type, balance):
    response = client.post(
        "/api/v1/accounts",
        json={"owner_id": owner_id, "type": type, "branch_id": 1, "balance": balance},
        auth=login(username),
    )
    assert response.status_code == 201, response.text
    return response.json()
