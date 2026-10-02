# tests/test_accounts.py
# Staff open accounts; customers see only their own; staff see all.

from conftest import open_account


def numbers(response):
    return [a["account_number"] for a in response.json()]


def test_staff_open_accounts_with_a_generated_number(bank):
    account = open_account(bank, owner_id=2, type="savings", balance=150, as_="manager")
    assert account["account_number"] == "0000000004" # 10 digits, made by the server
    assert account["type"] == "SAVINGS" # any capitalisation accepted
    assert account["owner_id"] == 2
    assert open_account(bank, 2, "CHECKING", 0, as_="admin")["account_number"] == "0000000005"


def test_opening_rules(bank):
    def open_(**changes):
        body = {"owner_id": 1, "type": "CHECKING", "branch_id": 1, "balance": 0, **changes}
        return bank.post("/accounts", json=body, as_="teller")

    low_savings = open_(type="SAVINGS", balance=50)
    assert low_savings.status_code == 400
    assert "at least 100.00" in low_savings.json()["detail"]
    assert open_(type="CRYPTO").status_code == 400
    assert open_(balance=-5).status_code == 400
    assert open_(balance=10.555).status_code == 400
    assert open_(owner_id=99).json()["detail"] == "owner_id 99 does not exist"
    assert open_(branch_id=99).json()["detail"] == "Branch 99 does not exist"


def test_customer_list_only_shows_their_own_accounts(bank):
    assert numbers(bank.get("/accounts", as_="rohit")) == ["0000000001", "0000000002"]
    assert numbers(bank.get("/accounts", as_="mohit")) == ["0000000003"]
    # filters still work, but never reach past the customer's own accounts
    assert numbers(bank.get("/accounts", params={"min_balance": 300}, as_="rohit")) == ["0000000001"]
    assert numbers(bank.get("/accounts", params={"min_balance": 0}, as_="mohit")) == ["0000000003"]


def test_staff_see_all_accounts_and_can_filter(bank):
    for staff in ("teller", "manager", "admin"):
        assert numbers(bank.get("/accounts", as_=staff)) == ["0000000001", "0000000002", "0000000003"], staff
    rich = bank.get("/accounts", params={"branch_id": 1, "min_balance": 150}, as_="admin")
    assert numbers(rich) == ["0000000001", "0000000002"]
    assert bank.get("/accounts", params={"branch_id": 2}, as_="admin").json() == []


def test_customer_cannot_view_someone_elses_account(bank):
    assert bank.get("/accounts/0000000001", as_="rohit").json()["balance"] == 500
    assert bank.get("/accounts/0000000003", as_="rohit").status_code == 403
    assert bank.get("/accounts/0000000003", as_="teller").status_code == 200
    assert bank.get("/accounts/9999999999", as_="admin").status_code == 404
