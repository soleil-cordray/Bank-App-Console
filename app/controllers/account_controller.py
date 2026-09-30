# app/controllers/account_controller.py
# WAS Controllers/AccountController.py, which was all `pass` stubs
# REFS: 2.2 (POST /accounts), 2.3 (GET /accounts filters), 2.C

from fastapi import APIRouter, Depends

from app.dependencies import ALL_ROLES, STAFF, require_roles
from app.models.auth import CurrentUser

from app.models.account import AccountCreate, AccountResponse
from app.services.account_service import account_service

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=201)
def create_account(account: AccountCreate, _: CurrentUser = Depends(require_roles(*STAFF))):
    # WHO [5A.3]: staff open accounts
    # POST /api/v1/accounts (open new account) [2.2]
    return account_service.create_account(account)


@router.get("", response_model=list[AccountResponse])
def read_accounts(branch_id: int | None = None, min_balance: float | None = None,
                  _: CurrentUser = Depends(require_roles(*ALL_ROLES))):
    # WHO [5A.3]: any logged-in user
    # TODO [5A.3 part 2]: a CUSTOMER should only see their OWN accounts
    # GET /api/v1/accounts?branch_id=123&min_balance=1000 [2.3]
    return account_service.get_all_accounts(branch_id, min_balance)


@router.get("/{account_number}", response_model=AccountResponse)
def read_account(account_number: str, _: CurrentUser = Depends(require_roles(*ALL_ROLES))):
    # WHO [5A.3]: any logged-in user
    # TODO [5A.3 part 2]: a CUSTOMER should only see their OWN account
    # read one account [2.C]
    return account_service.get_account(account_number)

# REMOVED: PUT and DELETE /accounts/{id} (see the note in account_service.py)
