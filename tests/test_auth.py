# tests/test_auth.py
# Logging in, and the difference between a customer and the admin.

from conftest import ADMIN, customer_body, login


def test_no_login_is_401(bank):
    response = bank.get("/api/v1/accounts")
    assert response.status_code == 401


def test_wrong_password_is_401(bank):
    assert bank.get("/api/v1/accounts", auth=("rohit", "wrong-password")).status_code == 401
    assert bank.get("/api/v1/accounts", auth=("nobody", "password123")).status_code == 401
    assert bank.get("/api/v1/accounts", auth=("admin", "wrong-password")).status_code == 401


def test_admin_and_customer_can_both_log_in(bank):
    assert bank.get("/api/v1/customers", auth=ADMIN).status_code == 200
    assert bank.get("/api/v1/customers/me", auth=login("rohit")).status_code == 200


def test_sign_up_needs_no_login_and_never_returns_the_password(client):
    client.post("/api/v1/branches", json={"branch_code": "DT01", "location": "1 Main St"}, auth=ADMIN)

    response = client.post("/api/v1/customers", json=customer_body("rohit"))
    assert response.status_code == 201
    body = response.json()
    assert body["customer_id"] == 1
    assert body["username"] == "rohit"
    assert "password" not in body


def test_username_must_be_unique_and_admin_is_reserved(bank):
    assert bank.post("/api/v1/customers", json=customer_body("rohit")).status_code == 400
    response = bank.post("/api/v1/customers", json=customer_body("admin"))
    assert response.status_code == 400
    assert response.json()["detail"] == "That username is reserved"


def test_sign_up_validation(bank):
    assert bank.post("/api/v1/customers", json=customer_body("shortpw", password="abc")).status_code == 400
    assert bank.post("/api/v1/customers", json=customer_body("bad name!")).status_code == 400
    bad_email = {**customer_body("newbie"), "email": "not-an-email"}
    assert bank.post("/api/v1/customers", json=bad_email).status_code == 400
    no_branch = bank.post("/api/v1/customers", json=customer_body("newbie", branch_id=99))
    assert no_branch.status_code == 400
    assert no_branch.json()["detail"] == "Branch 99 does not exist"


def test_deactivated_customer_can_no_longer_log_in(bank):
    assert bank.delete("/api/v1/customers/1", auth=ADMIN).status_code == 200

    response = bank.get("/api/v1/customers/me", auth=login("rohit"))
    assert response.status_code == 403
    assert "deactivated" in response.json()["detail"]
