# app/controllers/account_controller.py
# WAS Controllers/AccountController.py, which was all `pass` stubs
# REFS: 2.2 (POST /accounts), 2.3 (GET /accounts filters), 2.C

# ACCESS: open = the customer (for themselves); view = admin (all) or customer (own);
#         deactivate = admin only

from fastapi import APIRouter, Depends

from app.auth import CurrentUser, admin_only, customer_only, get_current_user
from app.models.account import AccountCreate, AccountResponse
from app.services.account_service import account_service

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=201)
def create_account(account: AccountCreate, user: CurrentUser = Depends(customer_only)):
    # POST /api/v1/accounts (open new account) [2.2]
    return account_service.create_account(account, user.customer_id)


@router.get("", response_model=list[AccountResponse])
def read_accounts(
    branch_id: int | None = None,
    min_balance: float | None = None,
    user: CurrentUser = Depends(get_current_user),
):
    # GET /api/v1/accounts?branch_id=123&min_balance=1000 [2.3]
    # customers get only their own accounts back
    return account_service.get_all_accounts(branch_id, min_balance, user.scope())


@router.get("/{account_number}", response_model=AccountResponse)
def read_account(account_number: str, user: CurrentUser = Depends(get_current_user)):
    # read one account [2.C]
    return account_service.get_account(account_number, user.scope())


@router.delete("/{account_number}", response_model=AccountResponse)
def deactivate_account(account_number: str, admin: CurrentUser = Depends(admin_only)):
    # only the admin can close (deactivate) an account; nothing is removed
    return account_service.deactivate_account(account_number)
