# app/repositories/branch_repository.py
# WAS Repositories/BranchRepository.py
# REFS: 3.3 (non-direct/contract staff ratio over 20%)

from app.database import branches
from app.repositories.base_repository import ACTIVE_ONLY, BaseRepository


class BranchRepository(BaseRepository):
    def __init__(self):
            super().__init__(branches, "branch_id")

    def non_direct_staff_ratio_over(self, threshold):
        '''Find branches where non-direct/contract staff ratio exceeds 20%.'''
        # CONCEPTS:
        # - ratio = (staff != DIRECT, i.e., CONTRACT) / (all staff)
        # - branch returned only when its ratio is STRICTLY above 20% (0.20)
        # - a branch without staff_list counts as empty
        # PIPELINE:
        # 1. $match: active branches only
        # 2. $project: count everyone in staff_list, and count who is not DIRECT ($filter)
        # 3. $match: skip branches with no staff (avoids dividing by zero)
        # 4. $addFields: ratio = non-direct / total
        # 5. $match: keep ratio > threshold
        staff = {"$ifNull": ["$staff_list", []]}
        pipeline = [
            {"$match": ACTIVE_ONLY},
            {"$project": {
                "_id": 0,
                "branch_id": 1,
                "branch_code": 1,
                "total_staff": {"$size": staff},
                "non_direct_staff": {"$size": {"$filter": {
                    "input": staff, "as": "s",
                    "cond": {"$ne": ["$$s.employment_type", "DIRECT"]},
                }}},
            }},
            {"$match": {"total_staff": {"$gt": 0}}},
            {"$addFields": {"non_direct_ratio": {"$divide": ["$non_direct_staff", "$total_staff"]}}},
            {"$match": {"non_direct_ratio": {"$gt": threshold}}},
            {"$sort": {"branch_id": 1}},
        ]
        rows = list(self.collection.aggregate(pipeline))
        for row in rows:
            row["non_direct_ratio"] = round(row["non_direct_ratio"], 4)
        return rows


branch_repository = BranchRepository()
