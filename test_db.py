import os
import django
from django.db import connections
from django.db.utils import OperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trusted_platform.settings')
django.setup()

def check_db():
    db_conn = connections['default']
    try:
        c = db_conn.cursor()
        print("Successfully connected to the database!")
    except OperationalError as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_db()
