# backend/init_db.py
from database import engine, Base
import models
from sqlalchemy import text

print("Creating database tables...")
# Enable the pgvector extension first
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

# Create all tables
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
