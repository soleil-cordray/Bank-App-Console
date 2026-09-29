# Bank-App-Console

Backend REST API | CRUD MVC Flow

## Prerequisites

1. install dependencies ==>
    windows: pip install fastapi uvicorn pydantic
    mac: brew install fastapi uvicorn pydantic

## 🎯 Goal

Convert the existing ABC Digital Bank Java console application into a modular Python REST API using a layered architecture.

The Java application's core concepts (User, Customer, Account, SavingsAccount, and CheckingAccount) will be carried forward into the Python implementation.

### Architecture

```bash
HTTP Request
↓
Controller / Router
↓
Service / Business Logic
↓
Repository / Data Access
↓
Model
```

The first version will use in-memory data. A database can be added later without changing the overall architecture.

## 🛠️ Technology

- Python
- Flask
- REST API
- Layered / MVC architecture
- In-memory storage
- Postman / curl for testing
- API version: /api/v1

## 📁 Project Structure

```bash
bank-api/
│
├── app/
│   ├── controllers/       # HTTP routes
│   ├── services/          # Business logic
│   ├── repositories/      # Data access
│   ├── models/            # Domain objects
│   └── main.py            # Flask entry point
│
├── requirements.txt
├── README.md
└── .gitignore
```

### Layer Responsibilities

| Layer |	Responsibility |
| - | - |
| Controller	| HTTP requests, responses, status codes |
| Service	| Validation and business rules |
| Repository | Store/retrieve/update data |
| Model	| Customer, Account, Transaction, etc. |

## 🔄 Java → Python Mapping

| Java | Python |
| - | - |
| Main.main()	| app/main.py |
| Scanner	| HTTP JSON requests |
| ArrayList<Customer> |	Repository/in-memory storage |
| User | models/user.py |
| Customer | models/customer.py |
| Account | models/account.py |
| SavingsAccount | models/account.py |
| CheckingAccount | models/account.py |
| Console menus	| REST endpoints |
| System.out.println() | JSON responses |

The REST API replaces the console interaction; the underlying banking concepts remain.

## 👤 Customer API

| Method | Endpoint |	Purpose |
| - | - | - |
| POST |	/api/v1/customers	| Create customer |
| GET |	/api/v1/customers	| List customers |
| GET	| /api/v1/customers/{id} | Get customer |
| PUT	| /api/v1/customers/{id} | Update customer |
| DELETE | /api/v1/customers/{id}	| Deactivate customer |

**Example**:
```bash
POST /api/v1/customers
```
```json
{
    "name": "Rohit",
    "username": "rohit",
    "password": "rohit123"
}
```

## 💳 Account API

```bash
POST /api/v1/accounts
GET  /api/v1/accounts
```

**Example**:
```json
{
    "customer_id": 1,
    "branch_id": 123,
    "account_type": "SAVINGS",
    "initial_balance": 5000
}
```

**Account Types**:
```bash
CHECKING
SAVINGS
```

## 💸 Transaction API

**Transfer Money**:
```bash
POST /api/v1/transactions/transfer
```
```json
{
    "from_account_id": 101,
    "to_account_id": 102,
    "amount": 500
}
```

The service layer will **enforce**:
- Accounts exist
- Accounts are active
- Amount is greater than zero
- Sufficient balance exists
- Source balance is reduced
- Destination balance is increased
- Transaction is recorded

## 🏦 Branches

Branches will be added to support account filtering.
```bash
Branch
├── id
├── name
└── location
```

Accounts will reference a branch:
```bash
Account
├── id
├── customer_id
├── branch_id
├── account_type
└── balance
```

## 🔎 Filtering

**Accounts**:
```bash
GET /api/v1/accounts?branch_id=123&min_balance=1000
```

**Transactions**:
```bash
GET /api/v1/transactions?start_date=2026-01-01&type=TRANSFER
```

## 📊 HTTP Status Codes
| Status | Usage |
| - | - |
| 200	| Successful request |
| 201	| Resource created |
| 400	| Invalid request |
| 404	| Resource not found |
| 500	| Unexpected server error |

## 🗺️ Implementation Roadmap

### 1. Setup

- Create project ✅
- Create package structure ✅
- Create main.py ✅
- Run the API

### 1. Models

Implement:
```bash
User
Customer
Account
CheckingAccount
SavingsAccount
Branch
Transaction
```

### 3. Customer CRUD

Implement:
```bash
Repository
↓
Service
↓
Controller
```
for all customer endpoints.

### 4. Accounts

Add account creation, retrieval, and filtering.

### 5. Transactions

Implement money transfers and transaction history.

### 6. Branches & Filtering

Add branch relationships and query parameter filtering.

### 7. Error Handling & Testing

Using Postman or curl, verify:
```bash
200
201
400
404
500
```

## 🎯 End Goal

Transform:
```bash
Java Console Application
↓
Python REST API
↓
Controller
↓
Service
↓
Repository
↓
Models
↓
Future Database
```

The focus of Phase 02 is learning how to transform the existing single-flow Java banking application into a modular RESTful backend.
