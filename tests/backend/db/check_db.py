# backend/check_db.py
from sqlalchemy import inspect
from backend.db.database import engine

# Connect to the database and inspect it
inspector = inspect(engine)

# Get the names of all the tables
tables = inspector.get_table_names()

print("Tables currently in the database:")
for table in tables:
    print(f"- {table}")
