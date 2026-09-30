# AccountService.py
# Business logic for accounts. Controllers call these methods, and these methods call the repositories.
# Usage in a controller:
#     from Services.AccountService import account_service
#     account_service.get_all_accounts(branch_id=1, min_balance=1000)

from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from Models.Account import AccountCreate, AccountResponse
from Repositories.AccountRepository import account_repository
from Repositories.BranchRepository import branch_repository
from Repositories.UserRepository import user_repository

ACCOUNT_TYPES = ["CHECKING", "SAVINGS"]


class AccountService:
    def create_account(self, account: AccountCreate) -> AccountResponse:
        new_account = self._check_and_clean(account)
        try:
            saved = account_repository.create(new_account)
        except DuplicateKeyError:
            # database.py has a unique index on account_number
            raise HTTPException(status_code=409, detail="Account number is already in use")
        return AccountResponse.model_validate(saved)

    def get_all_accounts(
        self,
        branch_id: int | None = None,
        user_id: int | None = None,
        min_balance: float | None = None,
    ) -> list[AccountResponse]:
        # Only filter by what the caller actually sent, e.g. GET /accounts/?branch_id=1&min_balance=1000
        filters = {}
        if branch_id is not None:
            filters["branch_id"] = branch_id
        if user_id is not None:
            filters["user_id"] = user_id
        if min_balance is not None:
            filters["balance"] = {"$gte": min_balance}  # $gte = "greater than or equal to"
        return [AccountResponse.model_validate(a) for a in account_repository.get_all(filters)]

    def get_account_by_id(self, account_id: int) -> AccountResponse:
        return AccountResponse.model_validate(self._get_or_404(account_id))

    def update_account(self, account_id: int, account: AccountCreate) -> AccountResponse:
        current = self._get_or_404(account_id)

        # Money only moves through transactions, so there's always a record of it
        if account.balance != current["balance"]:
            raise HTTPException(
                status_code=400,
                detail=f"Balance can't be edited directly (current balance is {current['balance']}). "
                "Use POST /transactions/ to deposit or withdraw.",
            )

        changes = self._check_and_clean(account)
        try:
            updated = account_repository.update(account_id, changes)
        except DuplicateKeyError:
            raise HTTPException(status_code=409, detail="Account number is already in use")
        return AccountResponse.model_validate(updated)

    def delete_account(self, account_id: int) -> AccountResponse:
        current = self._get_or_404(account_id)

        # Like a real bank: empty the account before closing it
        if current["balance"] > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Account still holds {current['balance']:.2f}. Withdraw or transfer it before closing.",
            )

        deleted = account_repository.deactivate(account_id)
        return AccountResponse.model_validate(deleted)

    def _get_or_404(self, account_id):
        account = account_repository.get_by_id(account_id)
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        return account

    def _check_and_clean(self, account):
        # Checks shared by create and update. Returns the account as a dict, ready to save.
        # 400 (not 404) because the bad IDs are in the request body, not the URL
        if user_repository.get_by_id(account.user_id) is None:
            raise HTTPException(status_code=400, detail=f"User {account.user_id} does not exist")
        if branch_repository.get_by_id(account.branch_id) is None:
            raise HTTPException(status_code=400, detail=f"Branch {account.branch_id} does not exist")

        # Accept "savings" or "Savings", but always store "SAVINGS"
        account_type = account.account_type.upper()
        if account_type not in ACCOUNT_TYPES:
            raise HTTPException(status_code=400, detail=f"account_type must be one of {ACCOUNT_TYPES}")

        cleaned = account.model_dump()
        cleaned["account_type"] = account_type
        return cleaned


account_service = AccountService()
