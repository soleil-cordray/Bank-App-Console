# app/repositories/customer_repository.py
# WAS Repositories/UserRepository.py
# REFS: 3.1 (customers live in the `users` collection), 1.1

from app.database import users
from app.repositories.base_repository import BaseRepository

class CustomerRepository(BaseRepository):
    def __init__(self):
        # customer_id WAS user_id, collection is still `users`
        super().__init__(users, "customer_id")

customer_repository = CustomerRepository()
