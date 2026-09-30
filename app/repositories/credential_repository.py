# app/repositories/credential_repository.py
# NEW. Saves and loads logins (email + password_hash + role).
# REFS: 5A.1

from app.database import credentials
from app.repositories.base_repository import HIDE_MONGO_ID, BaseRepository


class CredentialRepository(BaseRepository):
    def __init__(self):
        super().__init__(credentials, "login_id")

    def get_by_email(self, email):
        # used by login: the email is the username
        return self.collection.find_one({"email": email, **self._active()}, HIDE_MONGO_ID)


credential_repository = CredentialRepository()
