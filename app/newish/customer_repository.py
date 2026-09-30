# app/repositories/customer_repository.py
# WAS Repositories/UserRepository.py
# REFS: 3.1 (customers live in the `users` collection), 1.1

from app.database import users
from app.repositories.base_repository import HIDE_MONGO_ID, BaseRepository

class CustomerRepository(BaseRepository):
    def __init__(self):
        # customer_id WAS user_id, collection is still `users`
        super().__init__(users, "customer_id")

    def get_by_username(self, username):
        # for logging in; includes deactivated customers so auth can say why (403)
        return self.collection.find_one({"username": username}, HIDE_MONGO_ID)

customer_repository = CustomerRepository()
