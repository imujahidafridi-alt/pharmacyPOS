from core.database import init_db, SessionLocal, engine
from core.models import Base, Unit, User
import core.security as security

# Drop old tables and create new database schema
print("Wiping existing PostgreSQL schema...")
Base.metadata.drop_all(bind=engine)
print("Creating new multi-unit database schema...")
init_db()

# Seed default data
db = SessionLocal()

# Add default user
if not db.query(User).filter_by(username='admin').first():
    admin = User(
        username='admin',
        password_hash=security.hash_password('admin123'),
        role='Admin'
    )
    db.add(admin)

# Seed default Units
default_units = ['Tablet', 'Capsule', 'Strip', 'Box', 'Bottle', 'Syrup (ml)', 'Injection']
for u in default_units:
    if not db.query(Unit).filter_by(name=u).first():
        db.add(Unit(name=u))

db.commit()
print("Database reset complete. Default units seeded.")
