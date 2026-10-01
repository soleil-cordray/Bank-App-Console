# app/create_admin.py
# NEW. Creates the FIRST admin login (run once, from the terminal).
# Why: registration only makes CUSTOMER logins, and only an ADMIN can make
# staff logins, so the very first ADMIN has to be made outside the API.
#
# Run from the project folder:   python -m app.create_admin
# REFS: 5A.1, 5A.3

from getpass import getpass

from pydantic import ValidationError

from app.database import create_indexes, verify_connection
from app.exceptions import BadRequestError
from app.models.auth import StaffLoginCreate
from app.services.auth_service import auth_service


def main():
    verify_connection()
    create_indexes()  # makes sure the unique email index exists
    email = input("Admin email: ")
    password = getpass("Admin password (min 8 characters, hidden while typing): ")
    try:
        request = StaffLoginCreate(email=email, password=password, role="ADMIN")
        admin = auth_service.create_staff_login(request)
    except ValidationError as error:
        print("Not created:", error.errors()[0]["msg"])
        return
    except BadRequestError as error:
        print("Not created:", error)
        return
    print(f"Created ADMIN login {admin.login_id} for {admin.email}")


if __name__ == "__main__":
    main()
