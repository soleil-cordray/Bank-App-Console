# UserService.py
# Business logic for users. Controllers call these methods, and these methods call the repositories.
# Usage in a controller:
#     from Services.UserService import user_service
#     user_service.create_user(user)

from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from Models.User import UserCreate, UserResponse
from Repositories.AccountRepository import account_repository
from Repositories.BranchRepository import branch_repository
from Repositories.UserRepository import user_repository


class UserService:
    def create_user(self, user: UserCreate) -> UserResponse:
        self._check_branch_exists(user.branch_id)
        try:
            saved = user_repository.create(user)
        except DuplicateKeyError:
            # database.py has a unique index on username, so MongoDB rejects repeats
            raise HTTPException(status_code=409, detail="Username is already taken")
        return UserResponse.model_validate(saved)

    def get_all_users(self, branch_id: int | None = None) -> list[UserResponse]:
        # Only filter by what the caller actually sent, e.g. GET /users/?branch_id=1
        filters = {}
        if branch_id is not None:
            filters["branch_id"] = branch_id
        return [UserResponse.model_validate(u) for u in user_repository.get_all(filters)]

    def get_user_by_id(self, user_id: int) -> UserResponse:
        return UserResponse.model_validate(self._get_or_404(user_id))

    def update_user(self, user_id: int, user: UserCreate) -> UserResponse:
        self._get_or_404(user_id)
        self._check_branch_exists(user.branch_id)
        try:
            updated = user_repository.update(user_id, user)
        except DuplicateKeyError:
            raise HTTPException(status_code=409, detail="Username is already taken")
        return UserResponse.model_validate(updated)

    def delete_user(self, user_id: int) -> UserResponse:
        self._get_or_404(user_id)

        # Don't leave accounts behind with no owner
        if account_repository.get_all({"user_id": user_id}):
            raise HTTPException(status_code=400, detail="User still has open accounts. Close them first.")

        deleted = user_repository.deactivate(user_id)
        return UserResponse.model_validate(deleted)

    def _get_or_404(self, user_id):
        user = user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def _check_branch_exists(self, branch_id):
        # 400 (not 404) because the bad ID is in the request body, not the URL
        if branch_repository.get_by_id(branch_id) is None:
            raise HTTPException(status_code=400, detail=f"Branch {branch_id} does not exist")


user_service = UserService()
