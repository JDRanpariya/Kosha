import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Dynamically find the path to the infra/secrets/db_password.txt file
# Assuming this file is inside the 'backend' folder, we go up one level to the root, then into infra/secrets
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_FILE_PATH = os.path.join(BASE_DIR, "infra", "secrets", "db_password.txt")

# 2. Read the password securely from the file
try:
    with open(SECRET_FILE_PATH, "r") as f:
        DB_PASSWORD = f.read().strip()
except FileNotFoundError:
    raise Exception(f"Database password secret file not found at: {SECRET_FILE_PATH}")

# 3. Construct the connection URL using the loaded secret
SQLALCHEMY_DATABASE_URL = f"postgresql://kosha:{DB_PASSWORD}@localhost:5432/kosha_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
