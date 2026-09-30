# TransactionService.py
# Business logic for transactions. Saving a transaction also moves the money between accounts:
#     Deposit:    only account_id_to is set    -> money comes into that account
#     Withdrawal: only account_id_from is set  -> money leaves that account
#     Transfer:   both are set                 -> money moves from one account to the other
# Usage in a controller:
#     from Services.TransactionService import transaction_service
#     transaction_service.create_transaction(transaction)

from datetime import date, datetime

from fastapi import HTTPException

from Models.Transaction import TransactionCreate, TransactionResponse
from Repositories.AccountRepository import account_repository
from Repositories.TransactionRepository import transaction_repository

# How each ?type= filter is looked up in MongoDB. None matches an empty account field.
TYPE_FILTERS = {
    "DEPOSIT": {"account_id_from": None, "account_id_to": {"$ne": None}},
    "WITHDRAWAL": {"account_id_from": {"$ne": None}, "account_id_to": None},
    "TRANSFER": {"account_id_from": {"$ne": None}, "account_id_to": {"$ne": None}},
}


class TransactionService:
    def create_transaction(self, transaction: TransactionCreate) -> TransactionResponse:
        self._check_valid(transaction)

        changes = {}
        self._add_changes(changes, transaction.account_id_from, transaction.account_id_to, transaction.amount)
        self._move_money(changes)

        saved = transaction_repository.create(transaction)
        return TransactionResponse.model_validate(saved)

    def get_all_transactions(
        self,
        account_id: int | None = None,
        start_date: date | None = None,
        transaction_type: str | None = None,
    ) -> list[TransactionResponse]:
        # Only filter by what the caller actually sent, e.g. GET /transactions/?start_date=2026-01-01&type=TRANSFER
        filters = {}
        if account_id is not None:
            # $or = match either side, so an account's history shows money going in and out
            filters["$or"] = [{"account_id_from": account_id}, {"account_id_to": account_id}]
        if start_date is not None:
            # Timestamps are saved as text like "2026-01-01T09:30:00", which sorts in date order
            filters["timestamp"] = {"$gte": start_date.isoformat()}
        if transaction_type is not None:
            type_filter = TYPE_FILTERS.get(transaction_type.upper())
            if type_filter is None:
                raise HTTPException(status_code=400, detail=f"type must be one of {list(TYPE_FILTERS)}")
            filters.update(type_filter)
        return [TransactionResponse.model_validate(t) for t in transaction_repository.get_all(filters)]

    def get_transaction_by_id(self, transaction_id: int) -> TransactionResponse:
        return TransactionResponse.model_validate(self._get_or_404(transaction_id))

    def update_transaction(self, transaction_id: int, transaction: TransactionCreate) -> TransactionResponse:
        old = self._get_or_404(transaction_id)
        self._check_valid(transaction)

        # Correcting a transaction = undo the old one, then apply the new one.
        # Undo by swapping from/to, so the money goes back where it came from.
        changes = {}
        self._add_changes(changes, old["account_id_to"], old["account_id_from"], old["amount"])
        self._add_changes(changes, transaction.account_id_from, transaction.account_id_to, transaction.amount)
        self._move_money(changes)

        updated = transaction_repository.update(transaction_id, transaction)
        return TransactionResponse.model_validate(updated)

    def delete_transaction(self, transaction_id: int) -> TransactionResponse:
        old = self._get_or_404(transaction_id)

        # Deleting = reversing it (a refund): swap from/to so the money goes back
        changes = {}
        self._add_changes(changes, old["account_id_to"], old["account_id_from"], old["amount"])
        self._move_money(changes)

        deleted = transaction_repository.deactivate(transaction_id)
        return TransactionResponse.model_validate(deleted)

    def _get_or_404(self, transaction_id):
        transaction = transaction_repository.get_by_id(transaction_id)
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction

    def _check_valid(self, transaction):
        # Rules the Pydantic model can't check on its own
        if transaction.account_id_from is None and transaction.account_id_to is None:
            raise HTTPException(status_code=400, detail="Set account_id_from, account_id_to, or both")
        if transaction.account_id_from == transaction.account_id_to:
            raise HTTPException(status_code=400, detail="Can't transfer money to the same account")
        if round(transaction.amount, 2) != transaction.amount:
            raise HTTPException(status_code=400, detail="amount can't have more than 2 decimal places")
        try:
            # The model checks the format; this catches impossible dates like 2026-13-45
            datetime.fromisoformat(transaction.timestamp)
        except ValueError:
            raise HTTPException(status_code=400, detail="timestamp is not a real date and time")

    def _add_changes(self, changes, account_from, account_to, amount):
        # Records how much each account's balance goes down (-) or up (+), e.g. {1: -50.0, 2: 50.0}
        if account_from is not None:
            changes[account_from] = changes.get(account_from, 0) - amount
        if account_to is not None:
            changes[account_to] = changes.get(account_to, 0) + amount

    def _move_money(self, changes):
        # Check EVERY account before saving ANY of them, so a failed check never leaves money half-moved
        new_balances = {}
        for account_id, change in changes.items():
            account = account_repository.get_by_id(account_id)
            if account is None:
                raise HTTPException(status_code=400, detail=f"Account {account_id} does not exist or is closed")

            new_balance = round(account["balance"] + change, 2)  # keep money to cents
            if new_balance < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient funds in account {account_id} (balance is {account['balance']:.2f})",
                )
            new_balances[account_id] = new_balance

        for account_id, new_balance in new_balances.items():
            account_repository.update(account_id, {"balance": new_balance})


transaction_service = TransactionService()
