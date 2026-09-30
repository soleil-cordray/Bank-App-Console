# Bank-App-Console

Python REST API for the ABC Digital Bank.

Flags in the code: ADDED, CHANGED, KEPT, REMOVED, and MOVED describe your old code. [x.y] is Chapter x, Step y. [x.C] is a line from Chapter x's Concepts. [not in rubric] means the workshop doesn't require it.

#### Contents
1. [Setup](#setup)
2. [Run](#run)
3. [Test](#test)
4. [Troubleshoot](#troubleshoot)

## Setup
> Once a teammate has committed a frozen requirements.txt, use `python -m pip install -r requirements.txt` for step 4 instead.
> Before Step 13, install MongoDB. Details for every system are in the workshop's [mongodb.md](https://github.com/becloudready/workshops/blob/master/workshops/fullstack-aws/chapters/02-BackendWithRestApi-CRUD-MVCFlow_Filter_Search/mongodb.md).

**Prerequisites**: [Python 3.10+](https://www.python.org/downloads/), [Git](https://git-scm.com/download/win).

### Linux/macOS
```bash
# 1. Ensure Tools Installed
git --version
python3 --version # requires 3.10+
brew install python git # if needed

# 2. Clone Project
git clone <https://github.com/soleil-cordray/Bank-App-Console.git> Bank-App-Console
cd Bank-App-Console

# 3. Run Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Packages
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn httpx pymongo pyjwt bcrypt python-multipart
```

### Windows
```bash
# 1. Ensure Tools Installed
git --version
python --version # requires 3.10+

# 2. Clone Project
git clone <https://github.com/soleil-cordray/Bank-App-Console.git> Bank-App-Console
cd Bank-App-Console

# 3a. Enable Scripts (if disabled; answer 'Y')
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# 3b. Run Virtual Environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 4. Install Packages
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn httpx pymongo pyjwt bcrypt python-multipart
```

## Run
> After Step 12 the last line becomes uvicorn app.main:app --reload. If a teammate changed requirements.txt, also run python -m pip install -r requirements.txt after the pull.

#### Steps
1. Visit local project copy's root
2. Activate the virtual environment
3. Apply shared project updates to local copy
4. Start API (Ctrl+C to stop)

### Linux/macOS
```bash
cd Bank-App-Console
source venv/bin/activate
git pull --rebase
uvicorn main:app --reload
```

### Windows
```bash
cd Bank-App-Console
.\venv\Scripts\Activate.ps1
git pull --rebase
uvicorn main:app --reload
```

## Test
> Complete after Step 11 builds `smoke_test.py`

#### While server running
1. Open http://127.0.0.1:8000/doc#, click **Authorize**, and log in with a demo login.
2. In a **second terminal**, activate the VE and run `python smoke_test.py`. It should end with `ALL RUBRIC CHECKS PASSED`.
3. Run the demo script: `bash demo.sh`.

## Logins & Permissions
Basic username + password login (no hashing or tokens yet). In `/docs`, click **Authorize** and enter a login.
- **Admin**: `admin` / `admin123` (change with `ADMIN_USERNAME` / `ADMIN_PASSWORD` in `.env`)
- **Customers**: sign up with `POST /api/v1/customers` (no login needed), then log in with that username + password

| | Customer | Admin |
| - | - | - |
| View profile, accounts, balances, transactions | Own only | Everyone's |
| Update profile | Own only | No |
| Open accounts, deposit, withdraw, transfer | From own accounts only | No |
| Deactivate a customer or account | No (`POST /customers/me/close-request` asks the admin) | Yes |
| Branches | View | Create, update, delete, analytics |

`401` = not logged in / wrong password, `403` = logged in but not allowed.

## Automated Tests
The tests use `mongomock` (a fake MongoDB in memory), so they work without MongoDB running:
```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Troubleshoot

#### Adding a Python package
```bash
python -m pip install <package> # install package
python -m pip freeze > requirements.txt # update requirements.txt
# commit, then inform the team
```

#### Teammate changed `requirements.txt`
```bash
# re-install packages from requirements.txt
python -m pip install -r requirements.txt
```

#### Virtual environment broken / Python upgraded
```bash
# delete the venv folder (OS-specific)
rm -rf venv # Linux/macOS
Remove-Item -Recurse -Force venv # PowerShell
# redo steps 3 and 4 of initial setup
```

#### Port 8000 already in use
```bash
uvicorn main:app --reload --port 8001 # next port
# now use :8001 in every URL
```
