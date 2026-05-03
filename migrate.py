from core.database import engine
from sqlalchemy import text

def run_migration():
    with engine.connect() as conn:
        try:
            # Check if using postgres
            if 'postgresql' in str(engine.url):
                conn.execute(text("ALTER TABLE medicines ADD COLUMN IF NOT EXISTS is_discountable INTEGER DEFAULT 1;"))
            else:
                conn.execute(text("ALTER TABLE medicines ADD COLUMN is_discountable INTEGER DEFAULT 1;"))
            conn.commit()
            print("Migration successful: Added is_discountable column.")
        except Exception as e:
            print(f"Migration error (might already exist): {e}")

if __name__ == "__main__":
    run_migration()
