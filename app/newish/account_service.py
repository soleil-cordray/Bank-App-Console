# app/services/account_service.py
# WAS Services/AccountService.py
# REFS: 2.2 (POST /accounts), 2.3 (GET /accounts filters), 1.2,
#       1.3 (accounts of a branch)

# PERMISSIONS: `owner_id` = the logged-in customer's ID (None = the admin, who sees everything).
# A customer only ever sees their own accounts and balances.

from app.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.account import Account, AccountCreate, AccountResponse
from app.repositories.account_repository import account_repository
from app.repositories.branch_repository import branch_repository
from app.repositories.customer_repository import customer_repository


class AccountService:
    def create_account(self, account: AccountCreate, customer_id: int) -> AccountResponse:
        # POST /accounts (open new account) [2.2]; customers open accounts for themselves only
        if account.owner_id != customer_id:
            raise ForbiddenError("You can only open accounts for yourself")
        # 400 (not 404) because the bad IDs are in the request body (not URL)
        if customer_repository.get_by_id(account.owner_id) is None:
            raise BadRequestError(f"owner_id {account.owner_id} does not exist")
        if branch_repository.get_by_id(account.branch_id) is None:
            raise BadRequestError(f"Branch {account.branch_id} does not exist")

        try:
            # build Account class first so its rules run
            opened = Account.new(account.type, account.owner_id, account.branch_id, account.balance)
        except ValueError as error:
            raise BadRequestError(str(error))

        saved = account_repository.create(opened.to_document())
        return AccountResponse.model_validate(saved)

    def get_all_accounts(
        self,
        branch_id: int | None = None,
        min_balance: float | None = None,
        owner_id: int | None = None,
    ) -> list[AccountResponse]:
        # GET /accounts?branch_id=123&min_balance=1000 [2.3]
        # only filter by what caller actually sent
        filters = {}
        if branch_id is not None:
            filters["branch_id"] = branch_id
        if min_balance is not None:
            # $gte = "greater than or equal to"
            filters["balance"] = {"$gte": min_balance}
        if owner_id is not None:
            # a customer's list only ever holds their own accounts
            filters["owner_id"] = owner_id
        return [AccountResponse.model_validate(a) for a in account_repository.get_all(filters)]

    def get_account(self, account_number: str, owner_id: int | None = None) -> AccountResponse:
        # read an Account [2.C] (admin: any; customer: only their own)
        account = self._get_or_404(account_number)
        if owner_id is not None and account["owner_id"] != owner_id:
            raise ForbiddenError("You can only view your own accounts")
        return AccountResponse.model_validate(account)

    def deactivate_account(self, account_number: str) -> AccountResponse:
        # DELETE /accounts/{number} (admin only); the record and balance are kept
        self._get_or_404(account_number)
        return AccountResponse.model_validate(account_repository.deactivate(account_number))

    def _get_or_404(self, account_number):
        account = account_repository.get_by_id(account_number)
        if account is None:
            raise NotFoundError("Account not found")
        return account


account_service = AccountService()
