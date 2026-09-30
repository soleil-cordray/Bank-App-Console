# tests/test_customers.py
# Customers see / update only themselves; only the admin can list or deactivate.

from conftest import ADMIN, login


def test_customer_sees_own_profile_with_accounts_list(bank):
    me = bank.get("/api/v1/customers/me", auth=login("rohit")).json()
    assert me["customer_id"] == 1
    assert me["accounts_list"] == ["0000000001", "0000000002"]

    assert bank.get("/api/v1/customers/1", auth=login("rohit")).status_code == 200


def test_customer_cannot_see_someone_else(bank):
    response = bank.get("/api/v1/customers/2", auth=login("rohit"))
    assert response.status_code == 403


def test_customer_cannot_list_all_customers(bank):
    assert bank.get("/api/v1/customers", auth=login("rohit")).status_code == 403


def test_admin_can_view_every_customer(bank):
    customers = bank.get("/api/v1/customers", auth=ADMIN).json()
    assert [c["username"] for c in customers] == ["rohit", "mohit"]
    assert bank.get("/api/v1/customers/2", auth=ADMIN).json()["name"] == "Mohit"


def test_admin_has_no_me_profile(bank):
    assert bank.get("/api/v1/customers/me", auth=ADMIN).status_code == 403


def test_customer_updates_own_info(bank):
    response = bank.put("/api/v1/customers/1", json={"email": "rohit.new@example.com"}, auth=login("rohit"))
    assert response.status_code == 200
    assert response.json()["email"] == "rohit.new@example.com"
    assert response.json()["name"] == "Rohit" # fields not sent stay the same

    bad_branch = bank.put("/api/v1/customers/1", json={"branch_id": 99}, auth=login("rohit"))
    assert bad_branch.status_code == 400


def test_nobody_else_can_update_a_customer(bank):
    # not another customer...
    assert bank.put("/api/v1/customers/2", json={"name": "Hacked"}, auth=login("rohit")).status_code == 403
    # ...and not the admin either
    assert bank.put("/api/v1/customers/2", json={"name": "Hacked"}, auth=ADMIN).status_code == 403
    assert bank.get("/api/v1/customers/2", auth=ADMIN).json()["name"] == "Mohit"


def test_customer_cannot_delete_anyone_even_themselves(bank):
    assert bank.delete("/api/v1/customers/1", auth=login("rohit")).status_code == 403
    assert bank.delete("/api/v1/customers/2", auth=login("rohit")).status_code == 403
    assert bank.get("/api/v1/customers/1", auth=ADMIN).json()["is_active"] is True


def test_close_request_then_admin_deactivates(bank):
    # 1. the customer asks
    response = bank.post("/api/v1/customers/me/close-request", auth=login("rohit"))
    assert response.status_code == 200
    assert response.json()["close_requested"] is True

    # 2. the admin sees the pending request
    pending = bank.get("/api/v1/customers", params={"close_requested": True}, auth=ADMIN).json()
    assert [c["username"] for c in pending] == ["rohit"]

    # 3. the admin approves; the customer's accounts go inactive with them
    assert bank.delete("/api/v1/customers/1", auth=ADMIN).status_code == 200
    assert bank.get("/api/v1/customers/1", auth=ADMIN).status_code == 404
    numbers = [a["account_number"] for a in bank.get("/api/v1/accounts", auth=ADMIN).json()]
    assert numbers == ["0000000003"]


def test_missing_customer_is_404(bank):
    assert bank.get("/api/v1/customers/99", auth=ADMIN).status_code == 404
    assert bank.delete("/api/v1/customers/99", auth=ADMIN).status_code == 404
