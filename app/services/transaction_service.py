# app/services/transaction_service.py
# WAS Services/TransactionService.py
# REFS: 2.2 (transfer), 2.3 (transactions filters),
#       1.2 (uses deposit()/withdraw()), 1.4 (concurrent + negative),
#       1.C (transfer limit), 1.3 (monthly volume)

# Saving a transaction also moves the money between accounts:
# - DEPOSIT: only to_account is set -> money comes into that account
# - WITHDRAWAL: only from_account is set -> money leaves that account
# - TRANSFER: both are set -> money moves from one account to the other

from datetime import date, datetime, time

from app.exceptions import BadRequestError, NotFoundError
from app.models.account import Account
from app.models.transaction import Transaction, TransactionCreate, TransferCreate
from app.repositories.account_repository import account_repository
from app.repositories.branch_repository import branch_repository
from app.repositories.transaction_repository import transaction_repository

TRANSACTION_TYPES = ["DEPOSIT", "WITHDRAWAL", "TRANSFER"] # [1.1]

class TransactionService:
    # TRANSFER [2.2] ----------------------------------------------------------
    # POST /api/v1/transactions/transfer (process money transfer)
    def transfer(self, transfer: TransferCreate) -> Transaction:
        if transfer.from_account == transfer.to_account:
            raise BadRequestError("Can't transfer money to the same account.")
        if transfer.amount > Account.TRANSFER_LIMIT:
            raise BadRequestError(f"A single transfer can't be more than {Account.TRANSFER_LIMIT:.2f}.")

        source = self._load_account(transfer.from_account)
        destination = self._load_account(transfer.to_account)

        # STEP 1: ask Account objects
        # their rules (minimum balance, overdraft, positive amount)
        # give a clear error message BEFORE anything is saved
        self._ask(source.withdraw, transfer.amount)
        self._ask(destination.deposit, transfer.amount)

        # STEP 2: move money with one atomic database update per account
        # the check in step 1 used a balance that may be out of date, so db:
        # - repeats the check itself
        # - refuses if another request got there first.
        if not account_repository.change_balance(source.account_number, -transfer.amount, source.lowest_allowed_balance()):
            raise BadRequestError(f"Insufficient funds in account {source.account_number}")
        if not account_repository.change_balance(destination.account_number, transfer.amount, destination.lowest_allowed_balance()):
            # destination closed in the meantime: put the money back
            account_repository.change_balance(source.account_number, transfer.amount, source.lowest_allowed_balance())
            raise BadRequestError(f"Account {destination.account_number} does not exist or is closed")

        return self._record("TRANSFER", source.account_number, destination.account_number, transfer.amount, source.branch_id)

    # DEPOSIT / WITHDRAWAL ----------------------------------------------------
    # POST /api/v1/transactions
    def create_transaction(self, transaction: TransactionCreate) -> Transaction:
        if transaction.type == "DEPOSIT":
            account = self._load_account(transaction.to_account)
            self._ask(account.deposit, transaction.amount) # [1.2]
            self._change(account, transaction.amount)
            return self._record("DEPOSIT", None, account.account_number, transaction.amount, account.branch_id)
        account = self._load_account(transaction.from_account)

        # enforces minimum balance / overdraft [1.2]
        self._ask(account.withdraw, transaction.amount)
        # atomic, safe against simultaneous withdrawals [1.4]
        self._change(account, -transaction.amount)

        return self._record("WITHDRAWAL", account.account_number, None, transaction.amount, account.branch_id)

    # READ --------------------------------------------------------------------
    def get_all_transactions(self, start_date: date | None = None, type: str | None = None) -> list[Transaction]:
        # GET /transactions?start_date=2026-01-01&type=TRANSFER [2.3]
        # only filter by what the caller actually sent
        filters = {}
        if start_date is not None:
            # created_at is a real date/time now
            filters["created_at"] = {"$gte": datetime.combine(start_date, time.min)}
        if type is not None:
            type = type.upper()
            if type not in TRANSACTION_TYPES:
                raise BadRequestError(f"type must be one of {TRANSACTION_TYPES}")
            filters["type"] = type # now stored
        return [Transaction.model_validate(t) for t in transaction_repository.get_all(filters)]

    def get_transaction(self, id: int) -> Transaction:
        # read one transaction [2.C]
        transaction = transaction_repository.get_by_id(id)
        if transaction is None:
            raise NotFoundError("Transaction not found")
        return Transaction.model_validate(transaction)

    # ANALYTICS ---------------------------------------------------------------

    def branch_transaction_volume(self, branch_id: int, month: str) -> dict:
        '''Adds up the amount of EVERY transaction (deposits, withdrawals and transfers) that went through the branch in one month.'''
        if branch_repository.get_by_id(branch_id) is None:
            raise NotFoundError("Branch not found")
        try:
            year, month_number = (int(part) for part in month.split("-"))
            start = datetime(year, month_number, 1)
        except (ValueError, AttributeError):
            raise BadRequestError("month must look like 2026-09")
        end = datetime(year + 1, 1, 1) if month_number == 12 else datetime(year, month_number + 1, 1)

        in_month = transaction_repository.get_all(
            {"branch_id": branch_id, "created_at": {"$gte": start, "$lt": end}}
        )
        total = round(sum(t["amount"] for t in in_month), 2)
        return {"branch_id": branch_id, "month": month, "total_volume": total, "transaction_count": len(in_month)}

    def monthly_transfer_volume(self) -> list[dict]:
        # "Calculate monthly branch-wise transfer volumes." [3.3]
        return transaction_repository.monthly_transfer_volume()

    # HELPERS -----------------------------------------------------------------

    def _load_account(self, account_number):
        document = account_repository.get_by_id(account_number)
        if document is None:
            raise BadRequestError(f"Account {account_number} does not exist or is closed.")
        return Account.from_document(document)

    @staticmethod
    def _ask(action, amount):
        # run an Account method (deposit / withdraw); ValueError becomes a 400
        try:
            action(amount)
        except ValueError as error:
            raise BadRequestError(str(error))

    @staticmethod
    def _change(account, delta):
        if not account_repository.change_balance(account.account_number, delta, account.lowest_allowed_balance()):
            raise BadRequestError(f"Insufficient funds in account {account.account_number}")

    @staticmethod
    def _record(type, from_account, to_account, amount, branch_id):
        saved = transaction_repository.create({
            "type": type, "from_account": from_account, "to_account": to_account,
            "amount": amount, "branch_id": branch_id,
        })
        return Transaction.model_validate(saved)


transaction_service = TransactionService()
