
from app import app, db
from sqlalchemy import text

with app.app_context():
    print("Updating database schema...")
    
    # 1. Add columns to reports table
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE reports ADD COLUMN latitude FLOAT"))
            conn.execute(text("ALTER TABLE reports ADD COLUMN longitude FLOAT"))
            conn.commit()
        print("Added latitude/longitude columns to reports table.")
    except Exception as e:
        print(f"Columns might already exist or error: {e}")

    # 2. Create new tables (ReportAttachment)
    db.create_all()
    print("Created new tables (if any).")
