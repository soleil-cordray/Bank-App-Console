# app/controllers/branch_controller.py
# WAS Controllers/BranchController.py, which was all `pass` stubs
# REFS: 2.C (Managing ... Branches),
#       1.3 + 3.3 (the four analytics answers, exposed as GETs)

from fastapi import APIRouter, Query

from app.models.branch import Branch, BranchCreate, BranchUpdate
from app.services.branch_service import branch_service
from app.services.transaction_service import transaction_service

router = APIRouter(prefix="/branches", tags=["Branches"])


@router.post("", response_model=Branch, status_code=201)
def create_branch(branch: BranchCreate):
    return branch_service.create_branch(branch)


@router.get("", response_model=list[Branch])
def read_branches():
    return branch_service.get_all_branches()


@router.get("/{branch_id}", response_model=Branch)
def read_branch(branch_id: int):
    return branch_service.get_branch(branch_id)


@router.put("/{branch_id}", response_model=Branch)
def update_branch(branch_id: int, branch: BranchUpdate):
    return branch_service.update_branch(branch_id, branch)


@router.delete("/{branch_id}", response_model=Branch)
def deactivate_branch(branch_id: int):
    return branch_service.deactivate_branch(branch_id)


# ANALYTICS -------------------------------------------------------------------
# these four small read-only GETs exist so answers can show from Swagger/curl


@router.get("/analytics/transaction-volume", tags=["Analytics"])
def branch_transaction_volume(branch_id: int, month: str = Query(..., description="YYYY-MM, e.g. 2026-09")):
    # "total transaction volume for a branch per month" [1.3]
    return transaction_service.branch_transaction_volume(branch_id, month)


@router.get("/analytics/staff-to-manager-ratio", tags=["Analytics"])
def branches_over_staff_to_manager_ratio(limit: float = Query(..., ge=0)):
    # "staff-to-manager ratio over a specified limit" [1.3]
    return branch_service.branches_over_staff_to_manager_ratio(limit)


@router.get("/analytics/monthly-transfer-volume", tags=["Analytics"])
def monthly_transfer_volume():
    # "monthly branch-wise transfer volumes" [3.3]
    return transaction_service.monthly_transfer_volume()


@router.get("/analytics/non-direct-staff-ratio", tags=["Analytics"])
def branches_over_non_direct_ratio(threshold: float = Query(0.20, ge=0, le=1)):
    # "non-direct/contract staff ratio exceeds 20%" [3.3]
    return branch_service.branches_over_non_direct_ratio(threshold)
