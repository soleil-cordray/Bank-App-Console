# database.py
# One shared MongoDB connection for the whole app.
# Repositories import the collections from here, e.g.:
#     from database import users, accounts

import os

from dotenv import load_dotenv
from pymongo import MongoClient, ReturnDocument

# Read MONGO_URI and DB_NAME from the .env file in the project root
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "bank_app")

# Created once when this file is first imported.
# MongoClient keeps a connection pool, so every repository reuses it.
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

# Fail fast with a clear error if MongoDB isn't running
client.admin.command("ping")

db = client[DB_NAME]

# Collections (MongoDB creates them the first time a document is saved)
users = db["users"]
accounts = db["accounts"]
transactions = db["transactions"]
branches = db["branches"]

# Indexes for fast lookups (create_index does nothing if the index already exists)
accounts.create_index("account_number", unique=True)
accounts.create_index("branch_id")
users.create_index("username", unique=True)
users.create_index("branch_id")
transactions.create_index("timestamp")

# Counter so every new record gets the next number ID (1, 2, 3...),
# matching the int IDs in the models (user_id, account_id, ...)
counters = db["counters"]


def get_next_id(name):
    counter = counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return counter["value"]
