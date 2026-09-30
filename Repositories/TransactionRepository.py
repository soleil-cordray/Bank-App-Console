# TransactionRepository.py
# Saves and loads transactions in MongoDB. Usage in a service:
#     from Repositories.TransactionRepository import transaction_repository
#     transaction_repository.create(new_item)

from database import transactions
from Repositories.BaseRepository import BaseRepository


class TransactionRepository(BaseRepository):
    def __init__(self):
        super().__init__(transactions, "transaction_id")


transaction_repository = TransactionRepository()
