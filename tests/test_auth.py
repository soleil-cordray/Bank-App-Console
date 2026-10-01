# tests/test_auth.py
# Token login: register, log in, use the token, and every way a token can be refused.

from datetime import datetime, timedelta, timezone

import jwt

from app import database, security
from conftest import EMAILS, PASSWORD, customer_body


# LOGGING IN ------------------------------------------------------------------

def test_login_returns_a_signed_bearer_token(bank):
    response = bank.client.post("/api/v1/auth/login", data={"username": EMAILS["rohit"], "password": PASSWORD})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"

    # a JWT is three parts: header.payload.signature
    assert body["access_token"].count(".") == 2
    claims = security.decode_access_token(body["access_token"])
    assert claims["sub"] == "4" # rohit's login_id
    assert claims["email"] == EMAILS["rohit"]
    assert claims["roles"] == ["CUSTOMER"]
    assert claims["customer_id"] == 1
    assert claims["exp"] > claims["iat"]

    # the email is case-insensitive: "ROHIT@Example.COM" is the same login
    bank.log_in("rohit", email="ROHIT@Example.COM")
    assert bank.get("/auth/me", as_="rohit").status_code == 200


def test_auth_me_shows_who_the_token_belongs_to(bank):
    assert bank.get("/auth/me", as_="rohit").json()["role"] == "CUSTOMER"
    teller = bank.get("/auth/me", as_="teller").json()
    assert (teller["role"], teller["branch_id"], teller["customer_id"]) == ("TELLER", 1, None)


def test_wrong_password_and_unknown_email_get_the_same_401(bank):
    wrong_password = bank.client.post("/api/v1/auth/login", data={"username": EMAILS["rohit"], "password": "wrong-pass"})
    unknown_email = bank.client.post("/api/v1/auth/login", data={"username": "nobody@example.com", "password": PASSWORD})
    assert wrong_password.status_code == unknown_email.status_code == 401
    # same message, so nobody can use login to find out which emails exist
    assert wrong_password.json()["detail"] == unknown_email.json()["detail"] == "Invalid email or password"


# REFUSED TOKENS --------------------------------------------------------------

def test_no_token_is_401(bank):
    response = bank.get("/accounts")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_old_basic_login_no_longer_works(bank):
    # the previous version sent the username + password on every request;
    # now only a token is accepted
    response = bank.client.get("/api/v1/accounts", auth=(EMAILS["rohit"], PASSWORD))
    assert response.status_code == 401


def test_forged_garbage_or_orphaned_token_is_401(bank):
    future = datetime.now(timezone.utc) + timedelta(minutes=30)
    # signed with the wrong secret: someone trying to make their own ADMIN token
    forged = jwt.encode({"sub": "1", "roles": ["ADMIN"], "exp": future},
                        "an-attackers-guess-at-the-secret-key", algorithm="HS256")
    # correctly signed, but login 999 isn't in the database
    orphaned = security.create_access_token({"login_id": 999, "email": "ghost@bank.test", "role": "ADMIN"})
    for token in (forged, orphaned, "not-a-token", ""):
        response = bank.get("/accounts", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401, token


def test_expired_token_is_401(bank, monkeypatch):
    rohit_login = database.credentials.find_one({"email": EMAILS["rohit"]})
    monkeypatch.setattr(security, "JWT_EXPIRE_MINUTES", -1) # a token that expired a minute ago
    expired = security.create_access_token(rohit_login)

    response = bank.get("/accounts", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Token expired. Log in again."


def test_deactivated_customer_is_locked_out_immediately(bank):
    assert bank.delete("/customers/2", as_="admin").status_code == 200
    # the token mohit already has stops working right away...
    assert bank.get("/accounts", as_="mohit").status_code == 401
    # ...and he can't log in again
    response = bank.client.post("/api/v1/auth/login", data={"username": EMAILS["mohit"], "password": PASSWORD})
    assert response.status_code == 401


# REGISTERING -----------------------------------------------------------------

def test_register_needs_an_existing_customer_profile(bank):
    no_profile = bank.post("/auth/register", json={"email": "stranger@example.com", "password": PASSWORD})
    assert no_profile.status_code == 400

    twice = bank.post("/auth/register", json={"email": EMAILS["rohit"], "password": PASSWORD})
    assert twice.status_code == 400
    assert twice.json()["detail"] == "That email already has a login"

    bank.post("/customers", json=customer_body("sita"), as_="teller")
    short_password = bank.post("/auth/register", json={"email": "sita@example.com", "password": "short"})
    assert short_password.status_code == 400


def test_register_only_ever_makes_customer_logins(bank):
    bank.post("/customers", json=customer_body("sita"), as_="teller")
    # sneaking a role into the body does nothing
    response = bank.post("/auth/register", json={"email": "sita@example.com", "password": PASSWORD, "role": "ADMIN"})
    assert response.status_code == 201
    assert response.json()["role"] == "CUSTOMER"


def test_passwords_are_hashed_and_never_returned(bank):
    bank.post("/customers", json=customer_body("sita"), as_="teller")
    response = bank.post("/auth/register", json={"email": "sita@example.com", "password": PASSWORD})
    assert "password" not in response.json()
    assert "password_hash" not in response.json()

    saved = database.credentials.find_one({"email": "sita@example.com"})
    assert saved["password_hash"] != PASSWORD
    assert saved["password_hash"].startswith("$2b$") # a bcrypt hash


# STAFF LOGINS ----------------------------------------------------------------

def test_only_admin_creates_staff_logins(bank):
    body = {"email": "new.teller@bank.test", "password": PASSWORD, "role": "teller", "branch_id": 2}
    assert bank.post("/auth/staff", json=body).status_code == 401
    assert bank.post("/auth/staff", json=body, as_="rohit").status_code == 403
    assert bank.post("/auth/staff", json=body, as_="teller").status_code == 403

    created = bank.post("/auth/staff", json=body, as_="admin")
    assert created.status_code == 201
    assert created.json()["role"] == "TELLER" # any capitalisation accepted
    bank.log_in("new_teller", email="new.teller@bank.test")
    assert bank.get("/auth/me", as_="new_teller").json()["branch_id"] == 2


def test_staff_login_rules(bank):
    def staff(**changes):
        body = {"email": "x@bank.test", "password": PASSWORD, "role": "TELLER", "branch_id": 1, **changes}
        return bank.post("/auth/staff", json=body, as_="admin")

    assert staff(branch_id=None).status_code == 400 # a teller needs a branch
    assert staff(branch_id=99).status_code == 400 # the branch must exist
    assert staff(role="JANITOR").status_code == 400
    assert staff(email=EMAILS["teller"]).status_code == 400 # email already has a login
