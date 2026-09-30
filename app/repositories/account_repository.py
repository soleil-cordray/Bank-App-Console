# app/repositories/account_repository.py
# WAS Repositories/AccountRepository.py
# REFS: 1.4 (concurrent withdrawals), 1.1 (account_number),
#       2.2 (deactivating a customer)

from app.database import accounts, get_next_id
from app.repositories.base_repository import ACTIVE_ONLY, BaseRepository


class AccountRepository(BaseRepository):
    def __init__(self):
        # accounts identified by account_number (no separate account_id)
        super().__init__(accounts, "account_number")

    def _new_id(self):
        # every Account has an "Account Number"; the server generates it
        # so callers cannot clash; 10-digit format (e.g., "0000000001")
        return f"{get_next_id('account_number'):010d}"

    # [1.4]
    def change_balance(self, account_number, delta, lowest_allowed_balance):
        '''ReturnsTrue if balance was changed, False if change refused.'''
        # WITHDRAWAL HANDLING:
        # add `delta` to the balance (negative = withdraw) ONLY IF result
        # would still be at or above `lowest_allowed_balance`
        # CONCURRENCY HANDLING:
        # the check and the change happen in ONE atomic MongoDB operation
        result = self.collection.update_one(
            {
                "account_number": account_number,
                **ACTIVE_ONLY,
                "balance": {"$gte": round(lowest_allowed_balance - delta, 2)},   # balance + delta >= lowest
            },
            {"$inc": {"balance": delta}},
        )
        return result.modified_count == 1

    # [2.2]
    def deactivate_by_owner(self, owner_id):
        # a deactivated customer's accounts go inactive with them
        # (the records and balances are kept)
        result = self.collection.update_many(
            {"owner_id": owner_id, **ACTIVE_ONLY}, {"$set": {"is_active": False}}
        )
        return result.modified_count


account_repository = AccountRepository()
