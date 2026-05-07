import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from core.models import Base

# Load environment variables (if any)
load_dotenv()

# Determine connection URL
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost/pharmacy")

# SQLite needs connect_args for multithreading bypass, Postgres doesn't
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes the database schema if it doesn't exist."""
    print(f"Initializing database at: {DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    
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

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
