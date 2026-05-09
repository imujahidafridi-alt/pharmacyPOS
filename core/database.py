import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from core.models import Base

# Load environment variables (if any)
load_dotenv()

# Determine connection URL
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost/pharmacy")
SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO", "False").lower() in ("1", "true", "yes")

# SQLite needs connect_args for multithreading bypass, Postgres doesn't
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=SQLALCHEMY_ECHO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from contextlib import contextmanager


def sync_db_schema():
    """Adds any missing columns for existing tables so model changes do not require full migrations."""
    inspector = inspect(engine)
    with engine.connect() as connection:
        for table in Base.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                table.create(bind=engine, checkfirst=True)
                continue

            existing_columns = {col['name'] for col in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing_columns:
                    continue

                print(f"Auto-syncing missing column: {table.name}.{column.name}")
                col_type = column.type.compile(engine.dialect)
                connection.execute(text(f"ALTER TABLE {table.name} ADD COLUMN {column.name} {col_type}"))
                connection.commit()


def init_db():
    """Initializes the database schema if it doesn't exist and auto-syncs missing columns."""
    print(f"Initializing database at: {DATABASE_URL}")

    Base.metadata.create_all(bind=engine)
    sync_db_schema()
    
    # Insert default admin user if no users exist
    with SessionLocal() as db:
        from core.models import User
        if db.query(User).count() == 0:
            import core.security as security
            hashed_pw = security.hash_password('admin123')
            admin_user = User(username='admin', password_hash=hashed_pw, role='Admin')
            db.add(admin_user)
            db.commit()
    print("Database initialization complete.")

@contextmanager
def get_db_session():
    """Context manager to get a database session and ensure it closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db():
    """Dependency to get a database session. (Deprecated for context manager)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
