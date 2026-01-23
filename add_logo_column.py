from app import app, db
from sqlalchemy import text

with app.app_context():
    # Add logo column to service_providers table
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE service_providers ADD COLUMN logo VARCHAR(255)"))
            conn.commit()
            print("Successfully added 'logo' column to service_providers table.")
    except Exception as e:
        print(f"Error adding column (might already exist): {e}")
