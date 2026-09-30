# app/services/auth_service.py
# NEW. Registration and login.
# REFS: 5A.1 (registration + login, bcrypt), 5A.2 (issue JWT on login)

import re

from pymongo.errors import DuplicateKeyError

from app.exceptions import BadRequestError, UnauthorizedError
from app.models.auth import Login, RegisterRequest, Token
from app.repositories.credential_repository import credential_repository
from app.repositories.customer_repository import customer_repository
from app.security import create_access_token, hash_password, verify_password

# same message for "no such email" and "wrong password",
# so nobody can use login to find out which emails exist
BAD_LOGIN = "Invalid email or password"


class AuthService:
    # REGISTER [5A.1] ---------------------------------------------------------
    def register(self, request: RegisterRequest) -> Login:
        '''A customer creates a login for their existing customer profile.'''
        # anyone can call register, so it only ever creates CUSTOMER logins
        # TODO [5A.3 part 2]: a way to create TELLER / BRANCH_MANAGER / ADMIN logins
        customer = self._find_customer_by_email(request.email)
        if customer is None:
            raise BadRequestError("No customer profile uses that email. Ask a teller to create one first.")
        return self._save({
            "email": request.email,
            "password_hash": hash_password(request.password),
            "role": "CUSTOMER",
            "customer_id": customer["customer_id"],
            "branch_id": customer["branch_id"],
        })

    # LOGIN [5A.1, 5A.2] ------------------------------------------------------
    def login(self, email: str, password: str) -> Token:
        '''Check email + password, then hand back a signed token.'''
        login = credential_repository.get_by_email(email.strip().lower())
        if login is None or not verify_password(password, login["password_hash"]):
            raise UnauthorizedError(BAD_LOGIN)
        # a deactivated customer can't log in any more
        if login["role"] == "CUSTOMER" and customer_repository.get_by_id(login["customer_id"]) is None:
            raise UnauthorizedError(BAD_LOGIN)
        return Token(access_token=create_access_token(login))

    def get_login(self, login_id: int):
        # used on every request: is the token's login still allowed in?
        login = credential_repository.get_by_id(login_id)
        # a customer deactivated AFTER logging in loses access right away,
        # instead of when their token expires
        if login and login["role"] == "CUSTOMER" and customer_repository.get_by_id(login["customer_id"]) is None:
            return None
        return login

    # HELPERS -----------------------------------------------------------------

    def _save(self, document) -> Login:
        try:
            saved = credential_repository.create(document)
        except DuplicateKeyError:
            # database.py has a unique index on email
            raise BadRequestError("That email already has a login")
        return Login.model_validate(saved)  # Login has no password_hash field

    @staticmethod
    def _find_customer_by_email(email):
        # case-insensitive exact match ("Rohit@x.com" == "rohit@x.com")
        pattern = {"$regex": f"^{re.escape(email)}$", "$options": "i"}
        matches = customer_repository.get_all({"email": pattern})
        return matches[0] if matches else None


auth_service = AuthService()
