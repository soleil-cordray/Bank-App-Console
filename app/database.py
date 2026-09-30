# app/database.py
# One shared MongoDB connection for the whole app.
# REFS: 3.1 (collections + indexes), 3.2 (connection pooling)

import os

from dotenv import load_dotenv
from pymongo import MongoClient, ReturnDocument

# READ: from the .env file in the project root (MONGO_URI & DB_NAME)
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "bank_app")

# POOL [3.2]: now configured explicitly
# - single client created when this file is first imported
# - MongoClient keeps a connection pool, so every repository reuses it
client = MongoClient(
    MONGO_URI,
    maxPoolSize=50, # max 50 connections open at once [3.2]
    minPoolSize=5, # keep 5 warm so the first requests are fast [3.2]
    serverSelectionTimeoutMS=5000, # stop waiting >5s if MongoDB not running
)

db = client[DB_NAME]

# COLLECTIONS [3.1]: created the first time a document is saved
users = db["users"] # holds Customers ("users" is the name 3.1 requires)
accounts = db["accounts"]
transactions = db["transactions"]
branches = db["branches"]

# every new record gets the next number ID (1, 2, 3...)
counters = db["counters"]


def verify_connection():
    # a function ("is MongoDB running?") that main.py calls at startup
    client.admin.command("ping")


def create_indexes():
    # a function main.py calls at startup
    # (create_index does nothing if index already exists)

    # NAMED INDEXES [3.1]: uniqueness stops duplicates (safe identifiers)
    accounts.create_index("account_number", unique=True)
    branches.create_index("branch_code", unique=True)
    for collection in (users, accounts, transactions, branches):
        collection.create_index("created_at") # WAS timestamp (on transactions)

    # LOOKUP INDEXES [3.1]: identifiers & filters (fast queries)
    users.create_index("customer_id", unique=True)
    branches.create_index("branch_id", unique=True)
    transactions.create_index("id", unique=True)
    accounts.create_index("branch_id") # rubric-specified filter
    users.create_index("branch_id")
    # REMOVED users.create_index("username", unique=True)
    # > add later (when working on usernames/passwords)


def get_next_id(name):
    # atomic (non-concurrent) auto-increment
    counter = counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return counter["value"]
