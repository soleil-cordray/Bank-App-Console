# BranchService.py
# Business logic for branches. Controllers call these methods, and these methods call the repositories.
# Usage in a controller:
#     from Services.BranchService import branch_service
#     branch_service.get_all_branches()

from fastapi import HTTPException

from Models.Branch import BranchCreate, BranchResponse
from Repositories.AccountRepository import account_repository
from Repositories.BranchRepository import branch_repository
from Repositories.UserRepository import user_repository


class BranchService:
    def create_branch(self, branch: BranchCreate) -> BranchResponse:
        saved = branch_repository.create(branch)
        return BranchResponse.model_validate(saved)

    def get_all_branches(self) -> list[BranchResponse]:
        return [BranchResponse.model_validate(b) for b in branch_repository.get_all()]

    def get_branch_by_id(self, branch_id: int) -> BranchResponse:
        return BranchResponse.model_validate(self._get_or_404(branch_id))

    def update_branch(self, branch_id: int, branch: BranchCreate) -> BranchResponse:
        self._get_or_404(branch_id)
        updated = branch_repository.update(branch_id, branch)
        return BranchResponse.model_validate(updated)

    def delete_branch(self, branch_id: int) -> BranchResponse:
        self._get_or_404(branch_id)

        # A branch can't close while customers or accounts still belong to it
        if user_repository.get_all({"branch_id": branch_id}):
            raise HTTPException(status_code=400, detail="Branch still has users. Move or delete them first.")
        if account_repository.get_all({"branch_id": branch_id}):
            raise HTTPException(status_code=400, detail="Branch still has open accounts. Close them first.")

        deleted = branch_repository.deactivate(branch_id)
        return BranchResponse.model_validate(deleted)

    def _get_or_404(self, branch_id):
        branch = branch_repository.get_by_id(branch_id)
        if branch is None:
            raise HTTPException(status_code=404, detail="Branch not found")
        return branch


branch_service = BranchService()
