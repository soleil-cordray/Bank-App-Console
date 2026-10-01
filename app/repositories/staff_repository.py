from app.database import credentials
from app.repositories.base_repository import ACTIVE_ONLY, HIDE_MONGO_ID


class StaffRepository:
    STAFF_ROLES = ("TELLER", "BRANCH_MANAGER", "ADMIN")

    def get_by_branch_id(self, branch_id):
        records = credentials.find(
            {
                "branch_id": branch_id,
                "customer_id": None,
                "role": {"$in": self.STAFF_ROLES},
                **ACTIVE_ONLY,
            },
            HIDE_MONGO_ID,
        ).sort("login_id", 1)
        return list(records)


staff_repository = StaffRepository()