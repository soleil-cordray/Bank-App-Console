# AccountRepository.py
# Saves and loads accounts in MongoDB. Usage in a service:
#     from Repositories.AccountRepository import account_repository
#     account_repository.create(new_item)

from database import accounts
from Repositories.BaseRepository import BaseRepository


class AccountRepository(BaseRepository):
    def __init__(self):
        super().__init__(accounts, "account_id")


account_repository = AccountRepository()
