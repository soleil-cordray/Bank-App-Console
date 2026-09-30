# UserRepository.py
# Saves and loads users in MongoDB. Usage in a service:
#     from Repositories.UserRepository import user_repository
#     user_repository.create(new_item)

from database import users
from Repositories.BaseRepository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(users, "user_id")


user_repository = UserRepository()
