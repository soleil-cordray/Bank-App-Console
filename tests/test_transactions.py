# tests/test_transactions.py
# Money movement: customers only, from their own accounts; everyone sees only what they're allowed.

from conftest import ADMIN, login

ROHIT_CHECKING, ROHIT_SAVINGS, MOHIT_CHECKING = "0000000001", "0000000002", "0000000003"


def deposit(client, account, amount, auth):
    return client.post("/api/v1/transactions", json={"type": "DEPOSIT", "to_account": account, "amount": amount}, auth=auth)


def withdraw(client, account, amount, auth):
    return client.post("/api/v1/transactions", json={"type": "WITHDRAWAL", "from_account": account, "amount": amount}, auth=auth)


def transfer(client, source, destination, amount, auth):
    return client.post("/api/v1/transactions/transfer",
                       json={"from_account": source, "to_account": destination, "amount": amount}, auth=auth)


def balance(client, account):
    return client.get(f"/api/v1/accounts/{account}", auth=ADMIN).json()["balance"]


def test_deposit_and_withdrawal_change_the_balance(bank):
    response = deposit(bank, ROHIT_CHECKING, 25.50, login("rohit"))
    assert response.status_code == 201
    assert response.json()["type"] == "DEPOSIT"
    assert balance(bank, ROHIT_CHECKING) == 525.50

    assert withdraw(bank, ROHIT_CHECKING, 100, login("rohit")).status_code == 201
    assert balance(bank, ROHIT_CHECKING) == 425.50


def test_transfer_to_another_customer(bank):
    response = transfer(bank, ROHIT_CHECKING, MOHIT_CHECKING, 150, login("rohit"))
    assert response.status_code == 201
    assert response.json()["type"] == "TRANSFER"
    assert balance(bank, ROHIT_CHECKING) == 350
    assert balance(bank, MOHIT_CHECKING) == 250


def test_customer_cannot_move_someone_elses_money(bank):
    assert withdraw(bank, MOHIT_CHECKING, 10, login("rohit")).status_code == 403
    assert deposit(bank, MOHIT_CHECKING, 10, login("rohit")).status_code == 403
    response = transfer(bank, MOHIT_CHECKING, ROHIT_CHECKING, 10, login("rohit"))
    assert response.status_code == 403
    assert balance(bank, MOHIT_CHECKING) == 100


def test_forbidden_transfer_does_not_reveal_the_balance(bank):
    # even an impossible amount is refused for being someone else's account, not for funds
    response = transfer(bank, MOHIT_CHECKING, ROHIT_CHECKING, 9_000, login("rohit"))
    assert response.status_code == 403
    assert "balance" not in response.json()["detail"].lower()


def test_admin_cannot_make_transactions(bank):
    assert deposit(bank, ROHIT_CHECKING, 10, ADMIN).status_code == 403
    assert withdraw(bank, ROHIT_CHECKING, 10, ADMIN).status_code == 403
    assert transfer(bank, ROHIT_CHECKING, MOHIT_CHECKING, 10, ADMIN).status_code == 403
    assert balance(bank, ROHIT_CHECKING) == 500


def test_savings_minimum_balance(bank):
    response = withdraw(bank, ROHIT_SAVINGS, 101, login("rohit"))
    assert response.status_code == 400
    assert "INSUFFICIENT FUNDS" in response.json()["detail"]
    assert balance(bank, ROHIT_SAVINGS) == 200 # nothing changed
    assert withdraw(bank, ROHIT_SAVINGS, 100, login("rohit")).status_code == 201


def test_checking_overdraft_limit(bank):
    assert withdraw(bank, ROHIT_CHECKING, 1000, login("rohit")).status_code == 201 # 500 -> -500
    assert balance(bank, ROHIT_CHECKING) == -500
    assert withdraw(bank, ROHIT_CHECKING, 0.01, login("rohit")).status_code == 400


def test_transfer_rules(bank):
    same = transfer(bank, ROHIT_CHECKING, ROHIT_CHECKING, 10, login("rohit"))
    assert same.status_code == 400

    too_big = transfer(bank, ROHIT_CHECKING, ROHIT_SAVINGS, 10_000.01, login("rohit"))
    assert too_big.status_code == 400
    assert "10000.00" in too_big.json()["detail"]

    missing = transfer(bank, ROHIT_CHECKING, "9999999999", 10, login("rohit"))
    assert missing.status_code == 400
    assert balance(bank, ROHIT_CHECKING) == 500 # the failed transfer took nothing


def test_amount_and_shape_validation(bank):
    rohit = login("rohit")
    assert deposit(bank, ROHIT_CHECKING, -5, rohit).status_code == 400
    assert deposit(bank, ROHIT_CHECKING, 0, rohit).status_code == 400
    assert deposit(bank, ROHIT_CHECKING, 10.555, rohit).status_code == 400
    # a DEPOSIT needs to_account, a WITHDRAWAL needs from_account
    wrong_shape = bank.post("/api/v1/transactions",
                            json={"type": "DEPOSIT", "from_account": ROHIT_CHECKING, "amount": 10}, auth=rohit)
    assert wrong_shape.status_code == 400
    assert balance(bank, ROHIT_CHECKING) == 500


def test_deactivated_account_takes_no_transactions(bank):
    bank.delete(f"/api/v1/accounts/{MOHIT_CHECKING}", auth=ADMIN)
    assert transfer(bank, ROHIT_CHECKING, MOHIT_CHECKING, 10, login("rohit")).status_code == 400
    assert balance(bank, ROHIT_CHECKING) == 500


def test_customers_only_see_their_own_transactions(bank):
    deposit(bank, ROHIT_CHECKING, 10, login("rohit")) # id 1: rohit only
    deposit(bank, MOHIT_CHECKING, 10, login("mohit")) # id 2: mohit only
    transfer(bank, ROHIT_CHECKING, MOHIT_CHECKING, 5, login("rohit")) # id 3: both

    def ids(auth):
        return [t["id"] for t in bank.get("/api/v1/transactions", auth=auth).json()]

    assert ids(login("rohit")) == [1, 3]
    assert ids(login("mohit")) == [2, 3] # mohit sees money sent TO him too
    assert ids(ADMIN) == [1, 2, 3]

    assert bank.get("/api/v1/transactions/2", auth=login("rohit")).status_code == 403
    assert bank.get("/api/v1/transactions/2", auth=login("mohit")).status_code == 200
    assert bank.get("/api/v1/transactions/2", auth=ADMIN).status_code == 200
    assert bank.get("/api/v1/transactions/99", auth=ADMIN).status_code == 404


def test_transaction_filters(bank):
    deposit(bank, ROHIT_CHECKING, 10, login("rohit"))
    withdraw(bank, ROHIT_CHECKING, 10, login("rohit"))
    transfer(bank, ROHIT_CHECKING, MOHIT_CHECKING, 10, login("rohit"))

    def types(params):
        response = bank.get("/api/v1/transactions", params=params, auth=ADMIN)
        assert response.status_code == 200, response.text
        return [t["type"] for t in response.json()]

    assert types({"type": "transfer"}) == ["TRANSFER"]
    assert types({"type": "DEPOSIT"}) == ["DEPOSIT"]
    assert types({"start_date": "2000-01-01"}) == ["DEPOSIT", "WITHDRAWAL", "TRANSFER"]
    assert types({"start_date": "2999-01-01"}) == []
    assert bank.get("/api/v1/transactions", params={"type": "LOAN"}, auth=ADMIN).status_code == 400
