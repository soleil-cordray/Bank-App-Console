# Development

#### Contents
1. [Daily Workflow](#daily-workflow)
2. [Workshop Tracker](#workshop-tracker)
3. [Rubric](#rubric)

## Daily Workflow

#### Steps
1. Skim the [Workshop Map](). It lists what each chapter asks, with links to the instructor's files.
2. Find your rows in the [Rubric Tracker](). One row is one thing a grader can check. The middle column is the workshop's own wording; the last columns say where it is built and whether it is done.
3. Claim a track on the [Team Board]() by writing your name next to it.
4. Follow the [Build Steps]() for your rows, in order. Each step says what the file must contain and what "done" looks like.
5. Run the checks from [Step 11]() before every push.
6. Tick your tracker row and commit with the rubric ID: `git commit -m "[2.7] Add transfer endpoint".`

#### Before Every Push (Git)

```bash
git status # shows ready commits (review carefully)
git add . # add all files shown by git status
git commit -m "[2.8] MESSAGE" # [rubric ID] message
git pull --rebase # bring in teammates' work
python smoke_test.py # must pass
git push # send changes to shared repo
```

## Workshop Tracker

**Source**: [Workshop Chapters](https://github.com/becloudready/workshops/tree/master/workshops/fullstack-aws/chapters)

| File | Instructions | Rubric |
| - | - | - |
| [1. Fundamentals](https://github.com/becloudready/workshops/blob/master/workshops/fullstack-aws/chapters/01-Fundamentals-OOD-VibeCoding-LogicBuilding/01-Fundamentals-OOD-VibeCoding-LogicBuilding.md) | Entities, OOP account classes, business rules, three logic questions, AI edge cases | 1.1-1.8 |
| [2. Backend (REST API)](https://github.com/becloudready/workshops/blob/master/workshops/fullstack-aws/chapters/02-BackendWithRestApi-CRUD-MVCFlow_Filter_Search/02-BackendWithRestApi-CRUD-MVCFlow_Filter_Search.md) | Layered FastAPI API, `/api/v1` endpoints, filters, status codes | 2.1-2.11 |
| → [Optional App](https://github.com/becloudready/workshops/blob/master/workshops/fullstack-aws/chapters/02-BackendWithRestApi-CRUD-MVCFlow_Filter_Search/optional-extra-employee-app.md) & [Sample Project](https://github.com/becloudready/workshops/blob/master/workshops/fullstack-aws/chapters/02-BackendWithRestApi-CRUD-MVCFlow_Filter_Search/02-SampleReferenceProject.md) | Lab error cases and deliverables; reference project (MVC + dependency injection) | 2.12-2.13 |
| [3. Backend Integration](https://github.com/becloudready/workshops/blob/master/workshops/fullstack-aws/chapters/03-DatabaseConcepts-MongoDB-IntegrateWithRestApiBackend/03-DatabaseConcepts-MongoDB-IntegrateWithRestApiBackend.md) | Persistent MongoDB, indexes, pooling, aggregations | 3.1-3.9 |
| → [MongoDB](https://github.com/becloudready/workshops/blob/master/workshops/fullstack-aws/chapters/02-BackendWithRestApi-CRUD-MVCFlow_Filter_Search/mongodb.md) | Install MongoDB and use `mongosh` | 3.1 |
| 4-6. Testing, security, CI/CD | Postman and `pytest`; bcrypt, JWT, RBAC (mostly built early); GitHub Actions | TBD |

## Rubric

Each ID is a workshop step (e.g., 2.2 means Chapter 2, Step 2), and the heading is the workshop's focus. Each checkbox is one line from that step, word for word.

### 1. Fundamentals

#### 1.1 Classes & Attributes

- [ ] **Customer**: ID, Name, Email, Accounts list, Branch ID
- [ ] **Account**: Account Number, Type (Checking/Savings), Balance, Owner ID
- [ ] **Transaction**: ID, FromAccount, ToAccount, Amount, Timestamp, Type (Deposit/Withdrawal/Transfer)
- [ ] **Branch**: Branch Code, Location, Manager ID, Staff list

#### 1.2 Accounts Class

- [ ] `Account` class with methods: `deposit()`, `withdraw()`, `get_balance()`
- [ ] `SavingsAccount` extending `Account` with minimum balance enforcement
- [ ] `CheckingAccount` extending `Account` with overdraft limit logic

#### 1.3 Accounts Business Logic

- [ ] Which accounts belong to a specific branch?
- [ ] What is the total transaction volume for a branch per month?
- [ ] Which branches have a staff-to-manager ratio over a specified limit?

#### 1.4 Using AI

- [ ] Use an AI coding assistant to generate edge-case validation scenarios (e.g., concurrent withdrawal handling logic, negative inputs)
- [ ] Never leave AI unchecked

### 2. Backend (REST API)

#### 2.1 Architecture Setup

- [ ] `controllers/`: "API Router & Request Handling"
- [ ] `services/`: "Business & Domain Logic"
- [ ] `models/`: "In-Memory / DB Schemas"
- [ ] `main.py`: "Entry Point"
- [ ] `repositories/`: Data layer

#### 2.2 HTTP Methods (CRUD Endpoints)

- [ ] `POST /api/v1/customers`: Create customer profile
- [ ] `GET /api/v1/customers`: List customers
- [ ] `GET /api/v1/customers/{id}`: Get customer details
- [ ] `PUT /api/v1/customers/{id}`: Update info
- [ ] `DELETE /api/v1/customers/{id}`: Deactivate account
- [ ] `POST /api/v1/accounts`: Open new account
- [ ] `POST /api/v1/transactions/transfer`: Process money transfer

#### 2.3 Filtering & Search

- [ ] `GET /api/v1/accounts?branch_id=123&min_balance=1000`
- [ ] `GET /api/v1/transactions?start_date=2026-01-01&type=TRANSFER`

### 3. MongoDB

#### 3.1 Schema & Data Modeling

- [ ] Define MongoDB collections: `users`, `accounts`, `transactions`, `branches`
- [ ] Apply indexes: Index on `account_number`, `branch_code`, & `created_at` for high-performance querying
- [ ] Transition from in-memory storage to MongoDB

#### 3.2 Database Driver Integration
- [ ] Configure database client connection pooling (use *PyMongo*)
- [ ] Map incoming HTTP request bodies to MongoDB docs

#### 3.3 Advanced Queries & Aggregations
- [ ] Calculate monthly branch-wise transfer volumes
- [ ] Find branches where the non-direct/contract staff ratio exceeds 20%
