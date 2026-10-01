# app/services/branch_service.py
# WAS Services/BranchService.py
# REFS: 1.3 (staff-to-manager ratio), 3.3 (non-direct/contract ratio),
#       2.C (Managing ... Branches)

from pymongo.errors import DuplicateKeyError

from app.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.auth import Login
from app.models.branch import Branch, BranchCreate, BranchUpdate, validate_staff
from app.repositories.account_repository import account_repository
from app.repositories.branch_repository import branch_repository
from app.repositories.customer_repository import customer_repository
from app.repositories.staff_repository import staff_repository


class BranchService:
    # [2.C]
    def create_branch(self, branch: BranchCreate) -> Branch:
        try:
            saved = branch_repository.create(branch)
        except DuplicateKeyError:
            # database.py has a unique index on branch_code; rejects repeats
            raise BadRequestError("branch_code is already in use")
        return Branch.model_validate(saved)

    def get_all_branches(self) -> list[Branch]:
        return [Branch.model_validate(b) for b in branch_repository.get_all()]

    def get_branch(self, branch_id: int) -> Branch:
        return Branch.model_validate(self._get_or_404(branch_id))

    def get_branch_staff(self, branch_id: int, user=None) -> list[Login]:
        self._get_or_404(branch_id)
        if user is not None and user.role == "BRANCH_MANAGER" and user.branch_id != branch_id:
            raise ForbiddenError("You can only view staff at your own branch")
        return [Login.model_validate(login) for login in staff_repository.get_by_branch_id(branch_id)]

    def update_branch(self, branch_id: int, branch: BranchUpdate) -> Branch:
        current = self._get_or_404(branch_id)
        changes = branch.model_dump(exclude_none=True)
        try:
            # manager must be someone in the (new or existing) staff list
            validate_staff(changes.get("staff_list", current["staff_list"]),
                           changes.get("manager_id", current["manager_id"]))
        except ValueError as error:
            raise BadRequestError(str(error))
        try:
            updated = branch_repository.update(branch_id, changes)
        except DuplicateKeyError:
            raise BadRequestError("branch_code is already in use")
        return Branch.model_validate(updated)

    def deactivate_branch(self, branch_id: int) -> Branch:
        self._get_or_404(branch_id)
        # branch can't close while customers/accounts still belong to it
        if customer_repository.get_all({"branch_id": branch_id}):
            raise BadRequestError("Branch still has customers. Move or deactivate them first.")   # CHANGED wording: users -> customers
        if account_repository.get_all({"branch_id": branch_id}):
            raise BadRequestError("Branch still has open accounts. Close them first.")
        return Branch.model_validate(branch_repository.deactivate(branch_id))

    # ANALYTICS ---------------------------------------------------------------

    # [1.3]
    def branches_over_staff_to_manager_ratio(self, limit: float) -> list[dict]:
        '''Which branches have a staff-to-manager ratio over a specified limit?'''
        # a branch has ONE manager (manager_id, who is also in staff_list), so:
        # ratio = (people in staff_list NOT the manager) / (# of managers)
        # a branch with staff but no manager has no ratio at all; it is reported with ratio null (never divide by zero).
        flagged = []
        for branch in branch_repository.get_all():
            staff_ids = [member["staff_id"] for member in branch["staff_list"]]
            managers = 1 if branch["manager_id"] in staff_ids else 0
            others = len(staff_ids) - managers
            row = {"branch_id": branch["branch_id"], "branch_code": branch["branch_code"]}
            if managers == 0:
                if others > 0:
                    flagged.append({**row, "staff_to_manager_ratio": None, "note": "no manager"})
                continue
            ratio = round(others / managers, 2)
            if ratio > limit:
                flagged.append({**row, "staff_to_manager_ratio": ratio})
        return flagged

    def branches_over_non_direct_ratio(self, threshold: float) -> list[dict]:
        # find branches where non-direct/contract staff ratio exceeds 20%
        return branch_repository.non_direct_staff_ratio_over(threshold)

    def _get_or_404(self, branch_id):
        branch = branch_repository.get_by_id(branch_id)
        if branch is None:
            raise NotFoundError("Branch not found")
        return branch


branch_service = BranchService()
