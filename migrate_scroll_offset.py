#!/usr/bin/env python3
"""
Migration script to add scroll_offset_percent column to ReadingHistory table.
This enhances the image-based scroll restoration for very long images.
"""

import os
import sqlite3

def migrate_scroll_offset():
    """Add scroll_offset_percent column to ReadingHistory table if it doesn't exist."""
    
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
        
        if 'scroll_offset_percent' in columns:
            print("✅ scroll_offset_percent column already exists in ReadingHistory table")
            conn.close()
            return True
        
        # Add the scroll_offset_percent column
        print("📝 Adding scroll_offset_percent column to ReadingHistory table...")
        cursor.execute("ALTER TABLE reading_history ADD COLUMN scroll_offset_percent INTEGER DEFAULT 0")
        
        # Set all existing records to scroll_offset_percent = 0
        cursor.execute("UPDATE reading_history SET scroll_offset_percent = 0 WHERE scroll_offset_percent IS NULL")
        
        conn.commit()
        conn.close()
        
        print("✅ Successfully added scroll_offset_percent column")
        print("ℹ️ Enhanced scroll restoration for long images is now active")
        
    except Exception as e:
        print(f"❌ Error adding scroll_offset_percent column: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔄 Starting scroll_offset_percent migration...")
    
    if migrate_scroll_offset():
        print("✅ Migration completed successfully!")
        print("\nThe scroll restoration system now supports:")
        print("• Image-based positioning (which image you were viewing)")
        print("• Precise positioning within long images (scroll offset percentage)")
        print("• Works consistently across desktop and mobile devices")
    else:
        print("❌ Migration failed!")
        exit(1)