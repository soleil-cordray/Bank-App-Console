# BaseRepository.py
# Shared MongoDB logic used by every repository.
# Each repository only says which collection it uses and what its ID field is called.

from pymongo import ReturnDocument

from database import get_next_id

# Never send MongoDB's internal _id back to the API
HIDE_MONGO_ID = {"_id": 0}

# Deactivated records are hidden from normal reads
ACTIVE_ONLY = {"is_active": {"$ne": False}}


def _to_dict(data):
    # Accepts a Pydantic model (e.g. UserCreate) or a plain dict
    if hasattr(data, "model_dump"):
        return data.model_dump()
    return dict(data)


class BaseRepository:
    def __init__(self, collection, id_field):
        self.collection = collection  # e.g. users collection
        self.id_field = id_field      # e.g. "user_id"

    def create(self, data):
        # Save a new record and return it with its new ID
        document = _to_dict(data)
        document[self.id_field] = get_next_id(self.id_field)
        document["is_active"] = True
        self.collection.insert_one(document)
        return self.get_by_id(document[self.id_field])

    def get_by_id(self, record_id):
        # Return one active record, or None if not found
        query = {self.id_field: record_id, **ACTIVE_ONLY}
        return self.collection.find_one(query, HIDE_MONGO_ID)

    def get_all(self, filters=None):
        # Return all active records, optionally filtered, e.g. {"branch_id": 1}
        query = {**(filters or {}), **ACTIVE_ONLY}
        return list(self.collection.find(query, HIDE_MONGO_ID))

    def update(self, record_id, data):
        # Change fields on a record and return the updated version, or None if not found
        changes = _to_dict(data)
        changes.pop(self.id_field, None)  # the ID itself never changes
        return self.collection.find_one_and_update(
            {self.id_field: record_id, **ACTIVE_ONLY},
            {"$set": changes},
            projection=HIDE_MONGO_ID,
            return_document=ReturnDocument.AFTER,
        )

    def deactivate(self, record_id):
        # "Delete" = mark inactive instead of removing (per the rubric).
        # Returns the record as it was, or None if not found
        return self.collection.find_one_and_update(
            {self.id_field: record_id, **ACTIVE_ONLY},
            {"$set": {"is_active": False}},
            projection=HIDE_MONGO_ID,
        )
