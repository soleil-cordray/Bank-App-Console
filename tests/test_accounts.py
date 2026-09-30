# tests/test_accounts.py
# Customers open and see only their own accounts; the admin sees all and can deactivate.

from conftest import ADMIN, login


def numbers(response):
    return [a["account_number"] for a in response.json()]


def test_customer_opens_own_account_with_generated_number(bank):
    response = bank.post(
        "/api/v1/accounts",
        json={"owner_id": 2, "type": "savings", "branch_id": 1, "balance": 150},
        auth=login("mohit"),
    )
    assert response.status_code == 201
    account = response.json()
    assert account["account_number"] == "0000000004" # 10 digits, made by the server
    assert account["type"] == "SAVINGS" # any capitalisation accepted
    assert account["owner_id"] == 2


def test_customer_cannot_open_account_for_someone_else(bank):
    response = bank.post(
        "/api/v1/accounts",
        json={"owner_id": 2, "type": "CHECKING", "branch_id": 1, "balance": 0},
        auth=login("rohit"),
    )
    assert response.status_code == 403


def test_admin_cannot_open_accounts(bank):
    response = bank.post(
        "/api/v1/accounts",
        json={"owner_id": 1, "type": "CHECKING", "branch_id": 1, "balance": 0},
        auth=ADMIN,
    )
    assert response.status_code == 403


def test_opening_rules(bank):
    def open_(body):
        return bank.post("/api/v1/accounts", json={"owner_id": 1, "branch_id": 1, **body}, auth=login("rohit"))

    low_savings = open_({"type": "SAVINGS", "balance": 50})
    assert low_savings.status_code == 400
    assert "at least 100.00" in low_savings.json()["detail"]

    assert open_({"type": "CRYPTO", "balance": 0}).status_code == 400
    assert open_({"type": "CHECKING", "balance": -5}).status_code == 400
    assert open_({"type": "CHECKING", "balance": 10.555}).status_code == 400
    assert bank.post("/api/v1/accounts", json={"owner_id": 1, "type": "CHECKING", "branch_id": 99},
                     auth=login("rohit")).status_code == 400


def test_customer_list_only_shows_own_accounts(bank):
    assert numbers(bank.get("/api/v1/accounts", auth=login("rohit"))) == ["0000000001", "0000000002"]
    assert numbers(bank.get("/api/v1/accounts", auth=login("mohit"))) == ["0000000003"]
    # filters still apply, but never reach past the customer's own accounts
    assert numbers(bank.get("/api/v1/accounts", params={"min_balance": 300}, auth=login("rohit"))) == ["0000000001"]


def test_admin_sees_all_accounts_and_filters(bank):
    assert numbers(bank.get("/api/v1/accounts", auth=ADMIN)) == ["0000000001", "0000000002", "0000000003"]
    rich = bank.get("/api/v1/accounts", params={"branch_id": 1, "min_balance": 150}, auth=ADMIN)
    assert numbers(rich) == ["0000000001", "0000000002"]
    assert bank.get("/api/v1/accounts", params={"branch_id": 2}, auth=ADMIN).json() == []


def test_customer_cannot_view_someone_elses_account(bank):
    assert bank.get("/api/v1/accounts/0000000001", auth=login("rohit")).json()["balance"] == 500
    assert bank.get("/api/v1/accounts/0000000003", auth=login("rohit")).status_code == 403
    assert bank.get("/api/v1/accounts/0000000003", auth=ADMIN).status_code == 200
    assert bank.get("/api/v1/accounts/9999999999", auth=ADMIN).status_code == 404


def test_only_admin_can_deactivate_an_account(bank):
    assert bank.delete("/api/v1/accounts/0000000001", auth=login("rohit")).status_code == 403

    response = bank.delete("/api/v1/accounts/0000000001", auth=ADMIN)
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert bank.get("/api/v1/accounts/0000000001", auth=ADMIN).status_code == 404
    assert numbers(bank.get("/api/v1/accounts", auth=login("rohit"))) == ["0000000002"]
