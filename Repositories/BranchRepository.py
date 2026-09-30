# BranchRepository.py
# Saves and loads branches in MongoDB. Usage in a service:
#     from Repositories.BranchRepository import branch_repository
#     branch_repository.create(new_item)

from database import branches
from Repositories.BaseRepository import BaseRepository


class BranchRepository(BaseRepository):
    def __init__(self):
        super().__init__(branches, "branch_id")


branch_repository = BranchRepository()
