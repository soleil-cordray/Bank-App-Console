# app/repositories/base_repository.py
# WAS Repositories/BaseRepository.py
# REFS: 3.2 (request body -> MongoDB document), 3.1 (created_at)

from datetime import datetime, timezone

from pymongo import ReturnDocument

from app.database import get_next_id

HIDE_MONGO_ID = {"_id": 0} # never send MongoDB internal _id back to API
ACTIVE_ONLY = {"is_active": {"$ne": False}} # hide deactivated records

def _to_dict(data):
    # Accepts a Pydantic model (e.g. UserCreate) or a plain dict
    if hasattr(data, "model_dump"):
        return data.model_dump()
    return dict(data)

class BaseRepository:
    def __init__(self, collection, id_field, soft_delete=True):
        self.collection = collection # e.g., the users collection
        self.id_field = id_field # e.g., "customer_id"
        # transactions never deactivated, so they turn soft delete off
        self.soft_delete = soft_delete

    def _new_id(self):
        # split out so a repository can format its own IDs (accounts do)
        return get_next_id(self.id_field)

    def _active(self):
        return ACTIVE_ONLY if self.soft_delete else {}

    def create(self, data):
        # save a new record & return it with its new ID
        document = _to_dict(data)
        document[self.id_field] = self._new_id()
        document["created_at"] = datetime.now(timezone.utc) # server-set
        if self.soft_delete:
            document["is_active"] = True
        self.collection.insert_one(document)
        return self.get_by_id(document[self.id_field])

    def get_by_id(self, record_id):
        # return one active record (or None if not found)
        query = {self.id_field: record_id, **self._active()}
        return self.collection.find_one(query, HIDE_MONGO_ID)

    def get_all(self, filters=None):
        # return all active records, optionally filtered,
        # sorted by ID so lists always come back in the same order
        query = {**(filters or {}), **self._active()}
        return list(self.collection.find(query, HIDE_MONGO_ID).sort(self.id_field, 1))

    def update(self, record_id, data):
        # change record fields & return updated version (or None if not found)
        changes = _to_dict(data)
        changes.pop(self.id_field, None)  # the ID itself never changes
        if not changes: # reject empy $set
            return self.get_by_id(record_id)
        return self.collection.find_one_and_update(
            {self.id_field: record_id, **self._active()},
            {"$set": changes},
            projection=HIDE_MONGO_ID,
            return_document=ReturnDocument.AFTER,
        )

    def deactivate(self, record_id):
        # DELETE = atomic set inactive (no actual removal) [2.2]
        before = self.collection.find_one_and_update(
            {self.id_field: record_id, **self._active()},
            {"$set": {"is_active": False}},
            projection=HIDE_MONGO_ID,
        )
        return None if before is None else {**before, "is_active": False}
