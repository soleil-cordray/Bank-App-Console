# ============================================================================
# app/repositories/transaction_repository.py
# WAS Repositories/TransactionRepository.py
# REFS: 3.3 (monthly branch-wise transfer volumes), 1.1
# ============================================================================

from app.database import transactions
from app.repositories.base_repository import BaseRepository


class TransactionRepository(BaseRepository):
    def __init__(self):
        # soft delete is off: transactions never deactivated
        super().__init__(transactions, "id", soft_delete=False)

    # [3.3]
    def monthly_transfer_volume(self):
        '''Calculate monthly branch-wise transfer volumes'''
        # aggregation pipeline = list of stages (each stage feeds the next):
        # 1. $match: keep only TRANSFER transactions
        # 2. $group: one group per (branch_id, "YYYY-MM");
        #            add up the amounts and count them
        # 3. $sort: branch, then month
        # 4. $project: flatten the result into simple fields
        pipeline = [
            {"$match": {"type": "TRANSFER"}},
            {"$group": {
                "_id": {
                    "branch_id": "$branch_id",
                    "month": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}},
                },
                "total_transferred": {"$sum": "$amount"},
                "transfer_count": {"$sum": 1},
            }},
            {"$sort": {"_id.branch_id": 1, "_id.month": 1}},
            {"$project": {
                "_id": 0,
                "branch_id": "$_id.branch_id",
                "month": "$_id.month",
                "total_transferred": 1,
                "transfer_count": 1,
            }},
        ]
        rows = list(self.collection.aggregate(pipeline))
        for row in rows:
            row["total_transferred"] = round(row["total_transferred"], 2)   # hide float noise
        return rows


transaction_repository = TransactionRepository()
