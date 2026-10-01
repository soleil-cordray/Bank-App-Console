# tests/test_role_decisions.py
# RULES TO CONFIRM WITH THE TEAM
# Each test checks what the code does TODAY, where that differs from
# docs/DESIGN.md ("Role Capabilities"). If the team decides to change a rule,
# change the controller's require_roles(...) and flip the matching test.


def test_admin_can_deposit_and_withdraw(bank):
    # TODAY: transaction_controller allows require_roles("TELLER", "ADMIN")
    # DESIGN.md: admin "CANNOT deposit / withdraw / transfer"
    body = {"type": "DEPOSIT", "to_account": "0000000001", "amount": 10}
    assert bank.post("/transactions", json=body, as_="admin").status_code == 201


def test_admin_can_transfer_from_any_customers_account(bank):
    # TODAY: transfer allows require_roles("CUSTOMER", "ADMIN"), and only a
    #        CUSTOMER's ownership is checked, so an ADMIN can move anyone's money
    # DESIGN.md: admin "CANNOT deposit / withdraw / transfer"
    body = {"from_account": "0000000003", "to_account": "0000000001", "amount": 10}
    assert bank.post("/transactions/transfer", json=body, as_="admin").status_code == 201


def test_customer_cannot_update_their_own_profile(bank):
    # TODAY: PUT /customers/{id} is require_roles("ADMIN") only
    # DESIGN.md: a customer can "Update *own* profile"
    assert bank.put("/customers/1", json={"name": "Rohit S"}, as_="rohit").status_code == 403


def test_customer_cannot_open_their_own_accounts(bank):
    # TODAY: POST /accounts is STAFF only (a teller opens accounts for customers)
    # DESIGN.md: a customer can "Open extra accounts"
    body = {"owner_id": 1, "type": "CHECKING", "branch_id": 1, "balance": 0}
    assert bank.post("/accounts", json=body, as_="rohit").status_code == 403
