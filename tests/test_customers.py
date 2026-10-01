# tests/test_customers.py
# Staff create and list customers; a customer sees only their own profile;
# only the ADMIN updates or deactivates.

from conftest import customer_body


def test_staff_create_customers_and_customers_cannot(bank):
    for staff in ("teller", "manager", "admin"):
        body = customer_body(f"new_{staff}")
        response = bank.post("/customers", json=body, as_=staff)
        assert response.status_code == 201, staff
    assert bank.post("/customers", json=customer_body("sneaky"), as_="rohit").status_code == 403


def test_customer_creation_rules(bank):
    def create(**changes):
        return bank.post("/customers", json={**customer_body("sita"), **changes}, as_="teller")

    no_branch = create(branch_id=99)
    assert no_branch.status_code == 400
    assert no_branch.json()["detail"] == "Branch 99 does not exist"
    assert create(email="not-an-email").status_code == 400
    assert create(name="").status_code == 400


def test_customer_sees_only_their_own_profile(bank):
    me = bank.get("/customers/1", as_="rohit")
    assert me.status_code == 200
    assert me.json()["accounts_list"] == ["0000000001", "0000000002"]

    assert bank.get("/customers/2", as_="rohit").status_code == 403


def test_only_staff_list_customers(bank):
    for staff in ("teller", "manager", "admin"):
        customers = bank.get("/customers", as_=staff).json()
        assert [c["name"] for c in customers] == ["Rohit", "Mohit"], staff
    assert bank.get("/customers", as_="rohit").status_code == 403
    assert bank.get("/customers/2", as_="teller").json()["name"] == "Mohit"


def test_only_admin_updates_customers(bank):
    assert bank.put("/customers/2", json={"name": "Changed"}, as_="teller").status_code == 403
    assert bank.put("/customers/2", json={"name": "Changed"}, as_="manager").status_code == 403

    response = bank.put("/customers/2", json={"email": "mohit.new@example.com"}, as_="admin")
    assert response.status_code == 200
    assert response.json()["email"] == "mohit.new@example.com"
    assert response.json()["name"] == "Mohit" # fields not sent stay the same

    assert bank.put("/customers/2", json={"branch_id": 99}, as_="admin").status_code == 400


def test_only_admin_deactivates_customers(bank):
    assert bank.delete("/customers/1", as_="rohit").status_code == 403 # not even themselves
    assert bank.delete("/customers/2", as_="rohit").status_code == 403
    assert bank.delete("/customers/1", as_="teller").status_code == 403
    assert bank.delete("/customers/1", as_="manager").status_code == 403

    response = bank.delete("/customers/1", as_="admin")
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    # their accounts go inactive with them
    remaining = [a["account_number"] for a in bank.get("/accounts", as_="admin").json()]
    assert remaining == ["0000000003"]


def test_missing_customer_is_404(bank):
    assert bank.get("/customers/99", as_="admin").status_code == 404
    assert bank.put("/customers/99", json={"name": "Nobody"}, as_="admin").status_code == 404
    assert bank.delete("/customers/99", as_="admin").status_code == 404
