# app/controllers/account_controller.py
# WAS Controllers/AccountController.py, which was all `pass` stubs
# REFS: 2.2 (POST /accounts), 2.3 (GET /accounts filters), 2.C

from fastapi import APIRouter

from app.models.account import AccountCreate, AccountResponse
from app.services.account_service import account_service

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=201)
def create_account(account: AccountCreate):
    # POST /api/v1/accounts (open new account) [2.2]
    return account_service.create_account(account)


@router.get("", response_model=list[AccountResponse])
def read_accounts(branch_id: int | None = None, min_balance: float | None = None):
    # GET /api/v1/accounts?branch_id=123&min_balance=1000 [2.3]
    return account_service.get_all_accounts(branch_id, min_balance)


@router.get("/{account_number}", response_model=AccountResponse)
def read_account(account_number: str):
    # read one account [2.C]
    return account_service.get_account(account_number)

# REMOVED: PUT and DELETE /accounts/{id} (see the note in account_service.py)
