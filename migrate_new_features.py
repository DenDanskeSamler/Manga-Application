#!/usr/bin/env python3
"""
Database migration script to add new columns to existing databases.
Run this if you're having issues with missing columns.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from server.src.database.models import db, AppSettings
from server.app import app

def run_migrations():
    """Run database migrations to add new columns."""
    print("Starting database migration...")
    
    with app.app_context():
        try:
            # Create all tables first
            db.create_all()
            print("✓ Created/verified all tables")
            
            # Check and add bookmark columns
            table_name = 'bookmark'
            res = db.session.execute(text(f"PRAGMA table_info({table_name});")).fetchall()
            existing_cols = [r[1] for r in res]
            
            altered = False
            if 'chapter_number' not in existing_cols:
                db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN chapter_number INTEGER"))
                altered = True
                print("✓ Added chapter_number column to bookmark table")
                
            if 'chapter_title' not in existing_cols:
                db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN chapter_title VARCHAR(200)"))
                altered = True
                print("✓ Added chapter_title column to bookmark table")
                
            if altered:
                db.session.commit()
            
            # Check and add user columns
            user_table = 'user'
            res = db.session.execute(text(f"PRAGMA table_info({user_table});")).fetchall()
            existing_cols = [r[1] for r in res]
            
            altered = False
            if 'is_admin' not in existing_cols:
                db.session.execute(text(f"ALTER TABLE {user_table} ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL"))
                altered = True
                print("✓ Added is_admin column to user table")
                
            if 'is_disabled' not in existing_cols:
                db.session.execute(text(f"ALTER TABLE {user_table} ADD COLUMN is_disabled BOOLEAN DEFAULT 0 NOT NULL"))
                altered = True
                print("✓ Added is_disabled column to user table")
                
            # Guest column removed - no migration needed
                
            if altered:
                db.session.commit()
            
            # Initialize default settings
            if not AppSettings.query.first():
                default_settings = [
                    ('require_registration', 'false', 'Require user registration to access the site'),
                    ('max_users', '1000', 'Maximum number of users allowed')
                ]

                for key, value, description in default_settings:
                    setting = AppSettings(key=key, value=value, description=description)
                    db.session.add(setting)

                db.session.commit()
                print("✓ Initialized default settings")
            
            print("\n🎉 Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    return True

if __name__ == "__main__":
    if run_migrations():
        print("\nYou can now start the application normally.")
    else:
        print("\nPlease check the error messages above and try again.")
        sys.exit(1)