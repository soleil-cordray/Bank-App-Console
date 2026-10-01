#!/bin/sh
set -e

# Wait for MongoDB to be ready
echo "Waiting for MongoDB..."
python -c "
import sys
import time
from app.database import verify_connection

max_retries = 30
retry_count = 0
while retry_count < max_retries:
    try:
        verify_connection()
        print('MongoDB is ready!')
        sys.exit(0)
    except Exception as e:
        retry_count += 1
        if retry_count >= max_retries:
            print('Failed to connect to MongoDB after 30 retries')
            sys.exit(1)
        time.sleep(1)
"

# Create indexes
python -c "from app.database import create_indexes; create_indexes()"

# Check if any admin exists; if not, create one
echo "Checking for existing admins..."
python << 'PYTHON_EOF'
import os
from pymongo import MongoClient
from urllib.parse import urlparse

mongo_uri = os.getenv('MONGO_URI')
DB_NAME = os.getenv("DB_NAME")
# Parse the URI to extract database name
parsed = urlparse(mongo_uri)


client = MongoClient(mongo_uri)
db = client[DB_NAME]

admin_count = db['staff_login'].count_documents({'role': 'ADMIN'})

if admin_count == 0:
    print('No admins found. Creating default admin...')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@bank.local')
    admin_password = os.getenv('ADMIN_PASSWORD', 'AdminPassword123')
    
    from app.models.auth import StaffLoginCreate
    from app.services.auth_service import auth_service
    
    try:
        request = StaffLoginCreate(email=admin_email, password=admin_password, role='ADMIN')
        admin = auth_service.create_staff_login(request)
        print(f'✓ Created default ADMIN login {admin.login_id} ({admin_email})')
    except Exception as e:
        print(f'⚠ Admin creation failed: {e}')
else:
    print(f'✓ Found {admin_count} admin(s). Skipping admin creation.')
PYTHON_EOF

# Start the application
exec "$@"
