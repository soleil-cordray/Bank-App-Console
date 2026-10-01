# tests/test_transactions.py
# Tellers deposit / withdraw; customers transfer from their own accounts;
# everyone only sees the transactions they're allowed to.

ROHIT_CHECKING, ROHIT_SAVINGS, MOHIT_CHECKING = "0000000001", "0000000002", "0000000003"


def deposit(bank, account, amount, as_="teller"):
    return bank.post("/transactions", json={"type": "DEPOSIT", "to_account": account, "amount": amount}, as_=as_)


def withdraw(bank, account, amount, as_="teller"):
    return bank.post("/transactions", json={"type": "WITHDRAWAL", "from_account": account, "amount": amount}, as_=as_)


def transfer(bank, source, destination, amount, as_):
    body = {"from_account": source, "to_account": destination, "amount": amount}
    return bank.post("/transactions/transfer", json=body, as_=as_)


def balance(bank, account):
    return bank.get(f"/accounts/{account}", as_="admin").json()["balance"]


# MOVING MONEY ----------------------------------------------------------------

def test_teller_deposits_and_withdraws(bank):
    response = deposit(bank, ROHIT_CHECKING, 25.50)
    assert response.status_code == 201
    assert response.json()["type"] == "DEPOSIT"
    assert balance(bank, ROHIT_CHECKING) == 525.50

    assert withdraw(bank, ROHIT_CHECKING, 100).status_code == 201
    assert balance(bank, ROHIT_CHECKING) == 425.50


def test_customers_and_managers_cannot_deposit_or_withdraw(bank):
    for who in ("rohit", "manager"):
        assert deposit(bank, ROHIT_CHECKING, 10, as_=who).status_code == 403, who
        assert withdraw(bank, ROHIT_CHECKING, 10, as_=who).status_code == 403, who
    assert balance(bank, ROHIT_CHECKING) == 500


def test_customer_transfers_to_another_customer(bank):
    response = transfer(bank, ROHIT_CHECKING, MOHIT_CHECKING, 150, as_="rohit")
    assert response.status_code == 201
    assert response.json()["type"] == "TRANSFER"
    assert balance(bank, ROHIT_CHECKING) == 350
    assert balance(bank, MOHIT_CHECKING) == 250


def test_customer_cannot_transfer_someone_elses_money(bank):
    response = transfer(bank, MOHIT_CHECKING, ROHIT_CHECKING, 50, as_="rohit")
    assert response.status_code == 403
    assert balance(bank, MOHIT_CHECKING) == 100

    # even an impossible amount is refused as "not yours", which never reveals the balance
    response = transfer(bank, MOHIT_CHECKING, ROHIT_CHECKING, 9_000, as_="rohit")
    assert response.status_code == 403
    assert "balance" not in response.json()["detail"].lower()


def test_tellers_and_managers_cannot_transfer(bank):
    for who in ("teller", "manager"):
        assert transfer(bank, ROHIT_CHECKING, MOHIT_CHECKING, 10, as_=who).status_code == 403, who


# ACCOUNT RULES ---------------------------------------------------------------

def test_savings_minimum_balance(bank):
    response = withdraw(bank, ROHIT_SAVINGS, 101)
    assert response.status_code == 400
    assert "INSUFFICIENT FUNDS" in response.json()["detail"]
    assert balance(bank, ROHIT_SAVINGS) == 200 # nothing changed
    assert withdraw(bank, ROHIT_SAVINGS, 100).status_code == 201


def test_checking_overdraft_limit(bank):
    assert transfer(bank, ROHIT_CHECKING, ROHIT_SAVINGS, 1000, as_="rohit").status_code == 201 # 500 -> -500
    assert balance(bank, ROHIT_CHECKING) == -500
    assert transfer(bank, ROHIT_CHECKING, ROHIT_SAVINGS, 0.01, as_="rohit").status_code == 400


def test_transfer_rules(bank):
    assert transfer(bank, ROHIT_CHECKING, ROHIT_CHECKING, 10, as_="rohit").status_code == 400 # same account

    too_big = transfer(bank, ROHIT_CHECKING, ROHIT_SAVINGS, 10_000.01, as_="rohit")
    assert too_big.status_code == 400
    assert "10000.00" in too_big.json()["detail"]

    assert transfer(bank, ROHIT_CHECKING, "9999999999", 10, as_="rohit").status_code == 400
    assert balance(bank, ROHIT_CHECKING) == 500 # the failed transfers took nothing


def test_amount_and_shape_validation(bank):
    assert deposit(bank, ROHIT_CHECKING, -5).status_code == 400
    assert deposit(bank, ROHIT_CHECKING, 0).status_code == 400
    assert deposit(bank, ROHIT_CHECKING, 10.555).status_code == 400
    # a DEPOSIT needs to_account, a WITHDRAWAL needs from_account
    wrong_shape = bank.post("/transactions", json={"type": "DEPOSIT", "from_account": ROHIT_CHECKING, "amount": 10}, as_="teller")
    assert wrong_shape.status_code == 400
    assert balance(bank, ROHIT_CHECKING) == 500


def test_deactivated_account_takes_no_transactions(bank):
    bank.delete("/customers/2", as_="admin") # mohit and his account go inactive
    assert transfer(bank, ROHIT_CHECKING, MOHIT_CHECKING, 10, as_="rohit").status_code == 400
    assert deposit(bank, MOHIT_CHECKING, 10).status_code == 400
    assert balance(bank, ROHIT_CHECKING) == 500


# VIEWING ---------------------------------------------------------------------

def test_customers_only_see_their_own_transactions(bank):
    deposit(bank, ROHIT_CHECKING, 10) # id 1: rohit only
    deposit(bank, MOHIT_CHECKING, 10) # id 2: mohit only
    transfer(bank, ROHIT_CHECKING, MOHIT_CHECKING, 5, as_="rohit") # id 3: both

    def ids(who):
        return [t["id"] for t in bank.get("/transactions", as_=who).json()]

    assert ids("rohit") == [1, 3]
    assert ids("mohit") == [2, 3] # mohit sees money sent TO him too
    assert ids("teller") == ids("admin") == [1, 2, 3]

    assert bank.get("/transactions/2", as_="rohit").status_code == 403
    assert bank.get("/transactions/2", as_="mohit").status_code == 200
    assert bank.get("/transactions/2", as_="manager").status_code == 200
    assert bank.get("/transactions/99", as_="admin").status_code == 404


def test_transaction_filters(bank):
    deposit(bank, ROHIT_CHECKING, 10)
    withdraw(bank, ROHIT_CHECKING, 10)
    transfer(bank, ROHIT_CHECKING, MOHIT_CHECKING, 10, as_="rohit")

    def types(params, who="admin"):
        response = bank.get("/transactions", params=params, as_=who)
        assert response.status_code == 200, response.text
        return [t["type"] for t in response.json()]

    assert types({"type": "transfer"}) == ["TRANSFER"]
    assert types({"type": "DEPOSIT"}) == ["DEPOSIT"]
    assert types({"start_date": "2000-01-01"}) == ["DEPOSIT", "WITHDRAWAL", "TRANSFER"]
    assert types({"start_date": "2999-01-01"}) == []
    assert types({"type": "DEPOSIT"}, who="mohit") == [] # filters stay inside the customer's own
    assert bank.get("/transactions", params={"type": "LOAN"}, as_="admin").status_code == 400
