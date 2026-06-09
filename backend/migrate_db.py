from app.database import SessionLocal, engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE documents ADD COLUMN file_hash VARCHAR(64)"))
            conn.commit()
            print("Column file_hash added successfully")
        except Exception as e:
            print(f"Column file_hash might already exist: {e}")

if __name__ == "__main__":
    migrate()
