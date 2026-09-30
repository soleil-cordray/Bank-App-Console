# tests/test_branches.py
# Branch management (admin), branch viewing (anyone logged in), and the analytics.

from datetime import datetime, timezone

from conftest import ADMIN, login

STAFF = [
    {"staff_id": 1, "name": "Ann", "employment_type": "DIRECT"},
    {"staff_id": 2, "name": "Bob", "employment_type": "CONTRACT"},
    {"staff_id": 3, "name": "Cara", "employment_type": "CONTRACT"},
    {"staff_id": 4, "name": "Dev", "employment_type": "DIRECT"},
]


def make_branch(client, code, staff=(), manager_id=None):
    body = {"branch_code": code, "location": "9 High St", "manager_id": manager_id, "staff_list": list(staff)}
    return client.post("/api/v1/branches", json=body, auth=ADMIN)


def test_admin_branch_crud(client):
    created = make_branch(client, "UP02", STAFF, manager_id=1)
    assert created.status_code == 201
    assert created.json()["branch_id"] == 1

    updated = client.put("/api/v1/branches/1", json={"location": "10 High St"}, auth=ADMIN)
    assert updated.status_code == 200
    assert updated.json()["location"] == "10 High St"
    assert updated.json()["branch_code"] == "UP02" # fields not sent stay the same

    assert client.delete("/api/v1/branches/1", auth=ADMIN).status_code == 200
    assert client.get("/api/v1/branches/1", auth=ADMIN).status_code == 404


def test_branch_rules(client):
    make_branch(client, "UP02", STAFF, manager_id=1)
    assert make_branch(client, "UP02").status_code == 400 # duplicate code
    assert make_branch(client, "X1", STAFF, manager_id=9).status_code == 400 # manager not on staff
    # the same rule on update
    assert client.put("/api/v1/branches/1", json={"manager_id": 9}, auth=ADMIN).status_code == 400
    assert client.get("/api/v1/branches/99", auth=ADMIN).status_code == 404


def test_customers_can_view_but_not_change_branches(bank):
    rohit = login("rohit")
    assert bank.get("/api/v1/branches", auth=rohit).status_code == 200
    assert bank.get("/api/v1/branches/1", auth=rohit).status_code == 200
    assert bank.post("/api/v1/branches", json={"branch_code": "NEW", "location": "Somewhere"}, auth=rohit).status_code == 403
    assert bank.put("/api/v1/branches/1", json={"location": "Moved"}, auth=rohit).status_code == 403
    assert bank.delete("/api/v1/branches/1", auth=rohit).status_code == 403
    assert bank.get("/api/v1/branches").status_code == 401 # still need to log in


def test_cannot_close_a_branch_that_still_has_customers(bank):
    response = bank.delete("/api/v1/branches/1", auth=ADMIN)
    assert response.status_code == 400
    assert "customers" in response.json()["detail"]


def test_analytics_are_admin_only(bank):
    for url in (
        "/api/v1/branches/analytics/monthly-transfer-volume",
        "/api/v1/branches/analytics/non-direct-staff-ratio",
        "/api/v1/branches/analytics/staff-to-manager-ratio?limit=1",
        "/api/v1/branches/analytics/transaction-volume?branch_id=1&month=2026-09",
    ):
        assert bank.get(url, auth=login("rohit")).status_code == 403, url
        assert bank.get(url, auth=ADMIN).status_code == 200, url


def test_staff_ratio_analytics(client):
    make_branch(client, "UP02", STAFF, manager_id=1) # 3 staff per manager, 2 of 4 are contract
    make_branch(client, "SM03", STAFF[:2], manager_id=1) # 1 staff per manager, 1 of 2 contract
    make_branch(client, "DR04", [STAFF[0], STAFF[3]], manager_id=1) # 0 contract

    ratio = client.get("/api/v1/branches/analytics/staff-to-manager-ratio", params={"limit": 2}, auth=ADMIN).json()
    assert [(r["branch_code"], r["staff_to_manager_ratio"]) for r in ratio] == [("UP02", 3.0)]

    contract = client.get("/api/v1/branches/analytics/non-direct-staff-ratio", auth=ADMIN).json()
    assert [(r["branch_code"], r["non_direct_ratio"]) for r in contract] == [("UP02", 0.5), ("SM03", 0.5)]


def test_transaction_volume_analytics(bank):
    rohit = login("rohit")
    bank.post("/api/v1/transactions/transfer",
              json={"from_account": "0000000001", "to_account": "0000000003", "amount": 150}, auth=rohit)
    bank.post("/api/v1/transactions", json={"type": "DEPOSIT", "to_account": "0000000001", "amount": 50}, auth=rohit)
    this_month = datetime.now(timezone.utc).strftime("%Y-%m")

    monthly = bank.get("/api/v1/branches/analytics/monthly-transfer-volume", auth=ADMIN).json()
    assert monthly == [{"branch_id": 1, "month": this_month, "total_transferred": 150.0, "transfer_count": 1}]

    volume = bank.get("/api/v1/branches/analytics/transaction-volume",
                      params={"branch_id": 1, "month": this_month}, auth=ADMIN).json()
    assert volume["total_volume"] == 200.0
    assert volume["transaction_count"] == 2

    bad_month = bank.get("/api/v1/branches/analytics/transaction-volume",
                         params={"branch_id": 1, "month": "Sept"}, auth=ADMIN)
    assert bad_month.status_code == 400
