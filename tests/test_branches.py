# tests/test_branches.py
# Branch management (ADMIN), branch viewing (anyone logged in),
# and the analytics (BRANCH_MANAGER + ADMIN).

from datetime import datetime, timezone

STAFF = [
    {"staff_id": 1, "name": "Ann", "employment_type": "DIRECT"},
    {"staff_id": 2, "name": "Bob", "employment_type": "CONTRACT"},
    {"staff_id": 3, "name": "Cara", "employment_type": "CONTRACT"},
    {"staff_id": 4, "name": "Dev", "employment_type": "DIRECT"},
]
ANALYTICS = (
    "/branches/analytics/monthly-transfer-volume",
    "/branches/analytics/non-direct-staff-ratio",
    "/branches/analytics/staff-to-manager-ratio?limit=1",
    "/branches/analytics/transaction-volume?branch_id=1&month=2026-09",
)


def make_branch(api, code, staff=(), manager_id=None):
    body = {"branch_code": code, "location": "9 High St", "manager_id": manager_id, "staff_list": list(staff)}
    return api.post("/branches", json=body, as_="admin")


def test_admin_branch_crud(api):
    created = make_branch(api, "UP02", STAFF, manager_id=1)
    assert created.status_code == 201
    assert created.json()["branch_id"] == 1

    updated = api.put("/branches/1", json={"location": "10 High St"}, as_="admin")
    assert updated.status_code == 200
    assert updated.json()["location"] == "10 High St"
    assert updated.json()["branch_code"] == "UP02" # fields not sent stay the same

    assert api.delete("/branches/1", as_="admin").status_code == 200
    assert api.get("/branches/1", as_="admin").status_code == 404


def test_branch_rules(api):
    make_branch(api, "UP02", STAFF, manager_id=1)
    assert make_branch(api, "UP02").status_code == 400 # duplicate code
    assert make_branch(api, "X1", STAFF, manager_id=9).status_code == 400 # manager not on staff
    assert api.put("/branches/1", json={"manager_id": 9}, as_="admin").status_code == 400 # same rule on update
    assert api.get("/branches/99", as_="admin").status_code == 404


def test_everyone_logged_in_can_view_branches(bank):
    for who in ("rohit", "teller", "manager", "admin"):
        assert bank.get("/branches", as_=who).status_code == 200, who
        assert bank.get("/branches/1", as_=who).json()["branch_code"] == "DT01", who
    assert bank.get("/branches").status_code == 401 # but you do need a token


def test_only_admin_changes_branches(bank):
    for who in ("rohit", "teller", "manager"):
        assert bank.post("/branches", json={"branch_code": "NEW", "location": "Somewhere"}, as_=who).status_code == 403, who
        assert bank.put("/branches/1", json={"location": "Moved"}, as_=who).status_code == 403, who
        assert bank.delete("/branches/2", as_=who).status_code == 403, who


def test_cannot_close_a_branch_that_still_has_customers(bank):
    response = bank.delete("/branches/1", as_="admin")
    assert response.status_code == 400
    assert "customers" in response.json()["detail"]
    assert bank.delete("/branches/2", as_="admin").status_code == 200 # branch 2 is empty


# ANALYTICS -------------------------------------------------------------------

def test_analytics_are_for_managers_and_admin_only(bank):
    for url in ANALYTICS:
        assert bank.get(url, as_="manager").status_code == 200, url
        assert bank.get(url, as_="admin").status_code == 200, url
        assert bank.get(url, as_="teller").status_code == 403, url
        assert bank.get(url, as_="rohit").status_code == 403, url


def test_branch_manager_only_sees_their_own_branch_volume(bank):
    other_branch = "/branches/analytics/transaction-volume?branch_id=2&month=2026-09"
    assert bank.get(other_branch, as_="manager").status_code == 403
    assert bank.get(other_branch, as_="admin").status_code == 200


def test_staff_ratio_analytics(api):
    make_branch(api, "UP02", STAFF, manager_id=1) # 3 staff per manager; 2 of 4 contract
    make_branch(api, "SM03", STAFF[:2], manager_id=1) # 1 staff per manager; 1 of 2 contract
    make_branch(api, "DR04", [STAFF[0], STAFF[3]], manager_id=1) # nobody on contract

    ratio = api.get("/branches/analytics/staff-to-manager-ratio", params={"limit": 2}, as_="admin").json()
    assert [(r["branch_code"], r["staff_to_manager_ratio"]) for r in ratio] == [("UP02", 3.0)]

    contract = api.get("/branches/analytics/non-direct-staff-ratio", as_="admin").json()
    assert [(r["branch_code"], r["non_direct_ratio"]) for r in contract] == [("UP02", 0.5), ("SM03", 0.5)]


def test_transaction_volume_analytics(bank):
    bank.post("/transactions/transfer", json={"from_account": "0000000001", "to_account": "0000000003", "amount": 150}, as_="rohit")
    bank.post("/transactions", json={"type": "DEPOSIT", "to_account": "0000000001", "amount": 50}, as_="teller")
    this_month = datetime.now(timezone.utc).strftime("%Y-%m")

    monthly = bank.get("/branches/analytics/monthly-transfer-volume", as_="manager").json()
    assert monthly == [{"branch_id": 1, "month": this_month, "total_transferred": 150.0, "transfer_count": 1}]

    volume = bank.get("/branches/analytics/transaction-volume",
                      params={"branch_id": 1, "month": this_month}, as_="manager").json()
    assert volume["total_volume"] == 200.0
    assert volume["transaction_count"] == 2

    bad_month = bank.get("/branches/analytics/transaction-volume", params={"branch_id": 1, "month": "Sept"}, as_="admin")
    assert bad_month.status_code == 400
