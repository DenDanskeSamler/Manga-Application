#!/usr/bin/env python3
"""
Script to migrate the database and add is_admin column
"""
import sqlite3
from pathlib import Path

# Path to the database
db_path = Path(__file__).parent / "manga_app.db"

def migrate_database():
    """Add is_admin column to user table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if is_admin column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' not in columns:
            print("Adding is_admin column...")
            cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL")
            conn.commit()
            print("✓ is_admin column added successfully")
        else:
            print("✓ is_admin column already exists")
        
        # Show current users
        cursor.execute("SELECT id, username, email, is_admin, created_at FROM user")
        users = cursor.fetchall()
        
        if users:
            print("\n📋 Current Users:")
            print("ID | Username | Email | Admin | Created")
            print("-" * 60)
            for user in users:
                admin_status = "Yes" if user[3] else "No"
                print(f"{user[0]} | {user[1]} | {user[2]} | {admin_status} | {user[4] or 'N/A'}")
        else:
            print("No users found in database")
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

def make_user_admin(username):
    """Make a user admin"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update user to be admin
        cursor.execute("UPDATE user SET is_admin = 1 WHERE username = ?", (username,))
        
        if cursor.rowcount == 0:
            print(f"❌ User '{username}' not found")
        else:
            conn.commit()
            print(f"✓ User '{username}' is now an admin")
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2 and sys.argv[1] == "make-admin":
        username = sys.argv[2]
        migrate_database()
        make_user_admin(username)
    else:
        migrate_database()