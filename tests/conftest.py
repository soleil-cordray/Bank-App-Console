# tests/conftest.py
# pytest runs this automatically before the tests.
# - swaps the real MongoDB for mongomock (a fake MongoDB in memory), so the
#   tests work on any laptop without installing or starting MongoDB
# - logs every demo user in with a TOKEN (POST /api/v1/auth/login),
#   exactly like Swagger's "Authorize" button does

import os

import bcrypt
import mongomock
import pymongo
import pytest

# SETTINGS: fixed values for the tests, set BEFORE the app reads them
# (os.environ wins over .env, so a teammate's .env can't change the tests)
os.environ["JWT_SECRET"] = "test-only-secret-never-use-for-real"
os.environ["JWT_EXPIRE_MINUTES"] = "30"

# FAKE DATABASE: must happen BEFORE app.database is imported (it connects on import)
pymongo.MongoClient = mongomock.MongoClient

# FAST BCRYPT: real hashing is slow on purpose (good against attackers).
# The tests hash dozens of passwords, so they use the lowest cost (4 instead of 12).
_real_gensalt = bcrypt.gensalt
bcrypt.gensalt = lambda rounds=4, prefix=b"2b": _real_gensalt(rounds, prefix)

from fastapi.testclient import TestClient

from app import database
from app.main import app
from app.models.auth import StaffLoginCreate
from app.services.auth_service import auth_service

PASSWORD = "password123" # every demo login uses this
EMAILS = {
    "admin": "admin@bank.test",
    "teller": "teller@bank.test",
    "manager": "manager@bank.test",
    "rohit": "rohit@example.com",
    "mohit": "mohit@example.com",
}


class Bank:
    '''The test client, plus a saved token for each logged-in demo user.

    bank.get("/accounts", as_="rohit")  sends  Authorization: Bearer <rohit's token>
    bank.get("/accounts")               sends no token at all
    '''

    def __init__(self, client):
        self.client = client
        self.tokens = {} # name -> token

    def log_in(self, name, email=None, password=PASSWORD):
        # POST /api/v1/auth/login takes a FORM (username + password), not JSON;
        # the username is the email
        response = self.client.post(
            "/api/v1/auth/login",
            data={"username": email or EMAILS[name], "password": password},
        )
        assert response.status_code == 200, response.text
        self.tokens[name] = response.json()["access_token"]
        return self.tokens[name]

    def request(self, method, url, as_=None, headers=None, **kwargs):
        headers = dict(headers or {})
        if as_ is not None:
            headers["Authorization"] = f"Bearer {self.tokens[as_]}"
        return self.client.request(method, "/api/v1" + url, headers=headers, **kwargs)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)


@pytest.fixture
def api():
    '''An empty bank with only the first ADMIN login (logged in as "admin").'''
    # every test starts with empty collections, so IDs start at 1 again
    for name in database.db.list_collection_names():
        database.db[name].delete_many({})
    # `with` runs the app's startup (ping + create_indexes), like the real server
    with TestClient(app) as client:
        # the first admin can't be made through the API, so the tests do what
        # `python -m app.create_admin` does
        auth_service.create_staff_login(StaffLoginCreate(email=EMAILS["admin"], password=PASSWORD, role="ADMIN"))
        bank = Bank(client)
        bank.log_in("admin")
        yield bank


@pytest.fixture
def bank(api):
    '''A small bank used by most tests (everyone below is logged in):
         admin    ADMIN
         teller   TELLER at branch 1
         manager  BRANCH_MANAGER at branch 1
         branch 1 DT01, branch 2 UP02
         customer 1 rohit: 0000000001 CHECKING 500, 0000000002 SAVINGS 200
         customer 2 mohit: 0000000003 CHECKING 100
    '''
    for code in ("DT01", "UP02"):
        ok(api.post("/branches", json={"branch_code": code, "location": "1 Main St"}, as_="admin"))
    for name, role in (("teller", "TELLER"), ("manager", "BRANCH_MANAGER")):
        ok(api.post("/auth/staff", json={"email": EMAILS[name], "password": PASSWORD, "role": role, "branch_id": 1}, as_="admin"))
    api.log_in("teller")
    api.log_in("manager")

    # staff create the customer profiles; each customer then registers their own login
    for name in ("rohit", "mohit"):
        ok(api.post("/customers", json=customer_body(name), as_="teller"))
        ok(api.post("/auth/register", json={"email": EMAILS[name], "password": PASSWORD}))
        api.log_in(name)

    open_account(api, 1, "CHECKING", 500)
    open_account(api, 1, "SAVINGS", 200)
    open_account(api, 2, "CHECKING", 100)
    return api


# HELPERS ---------------------------------------------------------------------

def ok(response):
    # fail setup loudly (with the server's message) if a request didn't succeed
    assert response.status_code in (200, 201), response.text
    return response.json()


def customer_body(name, branch_id=1):
    return {"name": name.title(), "email": EMAILS.get(name, f"{name}@example.com"), "branch_id": branch_id}


def open_account(bank, owner_id, type, balance, as_="teller"):
    body = {"owner_id": owner_id, "type": type, "branch_id": 1, "balance": balance}
    return ok(bank.post("/accounts", json=body, as_=as_))
