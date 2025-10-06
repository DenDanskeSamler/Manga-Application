#!/usr/bin/env python3
"""
Migration script to add image_index column to ReadingHistory table.
This supports the new image-based scroll restoration system.
"""

import os
import sys
import sqlite3

def migrate_image_index():
    """Add image_index column to ReadingHistory table if it doesn't exist."""
    
    db_path = "manga_app.db"
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found. Make sure to run this from the project root.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(reading_history)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'image_index' in columns:
            print("✅ image_index column already exists in ReadingHistory table")
            conn.close()
            return True
        
        # Add the image_index column
        print("📝 Adding image_index column to ReadingHistory table...")
        cursor.execute("ALTER TABLE reading_history ADD COLUMN image_index INTEGER DEFAULT 0")
        
        # Set all existing records to image_index = 0
        cursor.execute("UPDATE reading_history SET image_index = 0 WHERE image_index IS NULL")
        
        conn.commit()
        conn.close()
        
        print("✅ Successfully added image_index column")
        print("ℹ️ All existing reading history entries will start from the first image (index 0)")
        
    except Exception as e:
        print(f"❌ Error adding image_index column: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔄 Starting image_index migration...")
    
    if migrate_image_index():
        print("✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Restart your manga application")
        print("2. The new image-based scroll system will be active")
        print("3. Old pixel-based scroll positions will be ignored")
    else:
        print("❌ Migration failed!")
        sys.exit(1)